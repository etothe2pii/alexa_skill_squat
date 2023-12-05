import os
import inflect
import time
from datetime import datetime
import json

def get_time():
    return datetime.now().strftime("%H_%M_%S")

class pair:

    def __init__(self, ground, gen, match):
        self.ground = ground
        self.gen = gen
        self.match = match

def extract_transcript(sequence):
    e = inflect.engine()
    


    s = sequence.lower().replace("exit skill", "").replace("i heard", "").replace(",", "").replace(".", "").replace("\n", "").split()
    
    new_s = []
    for i in range(len(s)):
        if s[i].isdigit():
            words = e.number_to_words(s[i]).replace("-", " ").split()
            new_s += words
        else:
            new_s.append(s[i])

    return s[:-1]

def extract_invocation(seqence):
    e = inflect.engine()
    s = seqence.lower().replace(",", "").replace("\n", "").replace(".", "").split()

    for i in range(len(s)):
        if s[i].isdigit():
            s[i] = e.number_to_words(s[i])

    return s

def compare_sequences(sequence_ground_truth, sequence_generated):

    intersect = set(sequence_ground_truth).intersection(sequence_generated)
    pairs = []

    if len(intersect) > 0:
        

        sect = list(intersect)[0]

        pairs.append(pair([sect], [sect], True))

        i_gnd = sequence_ground_truth.index(sect)
        i_gen = sequence_generated.index(sect)

        beg_gnd = sequence_ground_truth[:i_gnd]
        end_gnd = [] if i_gen > len(sequence_ground_truth) -2 else sequence_ground_truth[i_gen+1:]

        beg_gen = sequence_generated[:i_gen]
        end_gen = [] if i_gen > len(sequence_generated) -2 else sequence_generated[i_gen+1:]

        return compare_sequences(beg_gnd, beg_gen) + pairs + compare_sequences(end_gnd, end_gen)

    else:
        return [pair(sequence_ground_truth, sequence_generated, False)]
    

def do_analysis(transcript_dir, invocation_file, output_file):

    with open(invocation_file) as file:
        invocations = file.readlines()

        count = 0

    while True:
        files = os.listdir(transcript_dir)

        if len(files) > 0:

            print(f"{get_time()}:: extract_text:: {count} files complete out of {len(files) + count}. {count/(len(files) + count) * 100:.2f}% done.")

            f = files.pop(0)

            f_split = f.split(".")[0].split("_")
            accent = f_split[0]
            invocation = int(f_split[1])

            with open(f"{transcript_dir}{f}") as file:
                text = file.read()

            pairs = compare_sequences(extract_invocation(invocations[invocation]), extract_transcript(text))

            with open(output_file, "a") as results:
                for p in pairs:
                    results.write(accent)

                    s = f",{invocation},"

                    for g in p.ground:
                        s += f"{g} "
                    s += ","

                    for g in p.gen:
                        s+= f"{g} "
                    s += "\n"

                    results.write(s)

            os.rename(f"{transcript_dir}{f}", f"processed/{f}")
            count += 1
        else:
            time.sleep(5)



def do_word_analysis(text_dir, words_doc, results_file):
    with open(words_doc) as file:
        words = file.readlines()

    for i in range(len(words)):
        words[i] = words[i][:-1]

    count = 0
    files = os.listdir(text_dir)

    results = {}

    for f in files:
        print(f)
        split_up = f.split(".")[0].split("_")

        voice = split_up[0]
        word_num = int(split_up[1])

        

        if words[word_num] not in results.keys():
            results[words[word_num]] = {}
            
        if voice not in  results[words[word_num]].keys():
            results[words[word_num]][voice] = {}
        
        if words[word_num] not in  results[words[word_num]][voice].keys():
            results[words[word_num]][voice][words[word_num]] = 0

        if "NO AUDIO" not in  results[words[word_num]][voice].keys():
            results[words[word_num]][voice]["NO AUDIO"] = 0
        

        with open(f"{text_dir}{f}") as t:
            text = t.read()

        transcript = extract_transcript(text)


        if words[word_num] in transcript:

            results[words[word_num]][voice][words[word_num]] += 1

        elif len(transcript) == 0:
            results[words[word_num]][voice]["NO AUDIO"] += 1

        else:
            s = ""

            for t in transcript:
                s += t + " "

            if s not in  results[words[word_num]][voice].keys():
                results[words[word_num]][voice][s] = 0

            results[words[word_num]][voice][s] += 1


    with open(results_file, "w") as fp:
        json.dump(results, fp)
            
        
        
def analyze_results_json(results_file):

    with open(results_file) as r:
        results = json.load(r)

    count = 0

    total = 0

    counts = {}

    mild = []
    moderate = []
    high = []

    for k in results.keys():

        

        r = {}

        for k_1 in results[k].keys():
            for k_2 in results[k][k_1].keys():


                if k_2 not in r.keys():
                    r[k_2] = 0

                r[k_2] += results[k][k_1][k_2]

                if k_2 != "NO AUDIO":

                    for k_c in k_2.split():
                        if k_c not in counts.keys():
                            counts[k_c] = 0
                    
                    for k_c in k_2.split():
                        counts[k_c] += results[k][k_1][k_2]
        
        remove = []
        for k_r in r.keys():
            if r[k_r] <= 2 and k_r != k or k_r == "bluetooth " or k_r == "NO AUDIO":

                remove.append(k_r)
         

        for k_r in remove:
            r.pop(k_r)

        if len(r.keys()) > 1:
            
            # print(f"\"{k}\",", end="")
            print(f"{k}: {k}= {r[k]}", end = "")



            for k_r in r.keys():
                if k_r != k:
                    print(f", {k_r}= {r[k_r]}", end = "")
                    None

            print()

            count += 1

    print(f"Total concerns identified: {count}")
    print(f"Total words: {len(results.keys())}")

    printed = []
    for i in range(50):
        most = ""
        most_count = 0
        for k in counts.keys():
            if k not in printed:
                if counts[k] > most_count:
                    most = k
                    most_count = counts[k]
        
        printed.append(most)
        print(f"{most}: {most_count}")


    print("\n\n\n\n")
    print(high)
    print(moderate)
    print(mild)
    print("\n")
    print(len(high))
    print(len(moderate))
    print(len(mild))


    

if __name__ == "__main__":

    # files = os.listdir("raw_text")

    # with open("../bark-with-voice-clone/skills_clean.txt") as f:
    #     invocations = f.readlines()

    # for i in range(20):
    #     print(extract_invocation(invocations[i]))


    
    #do_analysis("raw_text/", "../bark-with-voice-clone/skills_clean.txt", "raw_results.txt")



    # do_word_analysis("word_raw_text/", "../bark-with-voice-clone/words.txt", "words_results.txt")
    analyze_results_json("words_results.txt")

