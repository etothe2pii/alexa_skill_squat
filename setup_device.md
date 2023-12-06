# AVS Python Interface

## Setup

The steps below outline the steps and resources I used to get this all working. It shouldn't be too complicated, a lot of it exists, just not in Python.

### 1 Set up your device

I'm assuming that you are likely going to be using this on a linux machine of some sort. I think it should work with a Raspberry Pi or just your laptop.

This will mostly follow the [official AVS docs](https://developer.amazon.com/en-US/docs/alexa/alexa-voice-service/get-started-with-alexa-voice-service.html), so I highly recommend taking a minute to familiarize yourself with that.

First, we need to register a device! Start by going to the [AVS Developer Console](https://developer.amazon.com/alexa/console/avs/products). (If you haven't already, sign up for an amazon developer account - it's free!) Click on "Add New Product", which takes you to the "Product Information" screen.

The Product Information screen lets you set some settings for your device. Set the product name and Product ID. We'll need the Product ID in a minute. Select Device With Alexa built-in. Other than that the settings shouldn't matter a ton.

### 2 Set up the Security Profile

If you haven't used AVS before, you'll have to create a new profile. Choose a name and a description. After hitting next, you'll see a new dashboard, including a security profile ID. You'll be able to access all this info later, so don't sweat trying to write down/remember everything. 

Since we're using code based linking, scroll down to platform information (the title shows up on the left side of the screen) and select the Other Devices and Platforms tab. Input a client ID name and click "Generate ID". A Client ID will appear. Again, this is all accessable later. You can also generate new Client IDs at any time.

Finally, agree to the services agreement and click "Finish".

### 3 Register Your Device

You will likely eventually wrap all of this inside your application (or whatever you're using this for), but for now we'll do this one step at a time. After you click "Finish" in the previous step you should be back at the [AVS Developer Console](https://developer.amazon.com/alexa/console/avs/products). Click on your device again. We will be needing some of the information we just entered/generated.

send_requests.py is your holy grail of connecting to AVS. For people that are familiar with this type of shenanigans I'm sure that this is a "no duh" moment for you, but before starting on this project I had no idea what was going on. So, I'll explain it to anyone like me :). 

send_requests.py can be used as a command line tool or a simple coding interface. It has three basic methods, post_auth_request, request_device_tokens, and request_token_refresh. Generally, the idea is post_auth_request -> request_device_tokens -> request_token_refresh -> request_token_refresh ...

The idea is that each sends a POST request to the AVS server and gets back a response with different codes and tokens. If you want more info on the specifics of this process, here's the [AVS Documentation on the topic](https://developer.amazon.com/en-US/docs/alexa/alexa-voice-service/authorize-cbl.html#).

To register your device you'll need to run send_requests.py with the --auth_request flag, which will require the parameters --client_id (found under the device's security profile -> other devices and platforms - there should be a field called Client ID) and --product_id (this is in your device's information, it's the ID you set in step 2). Optionally you can include --serial_number (which you can arbitrarily generate). For example:

```
python3 send_requests.py --auth_request --client_id amzn1.application-oa2-client.851d101c41de450280dda151810f1405 --product_id TestDev --serial_number 00001
```

This will generate a response like this:

```
{"user_code":"FUP8UN","device_code":"85581b0f-cf10-459e-b823-477a9220f958","interval":30,"verification_uri":"https://amazon.com/us/code","expires_in":600}
```

Note the user and device codes, we'll need it in a moment. Go to the [verification uri](https://amazon.com/us/code), sign into your account, and enter the user code (in this case that's "FUP8UN"). If everything went right, the device should be registered.

I ran into an error here for quite a while where it would respond with a generic error message after I entered the code. If this happens to you, it's likely that the product id or client id weren't set correctly. 

Next we need to get our access and refresh tokens. We can use send_requests.py --request_tokens for this. We need both the user and device codes from the previous step. The call should look something like this:

```
python3 send_requests.py --request_tokens --device_code 85581b0f-cf10-459e-b823-477a9220f958 --user_code FUP8UN
```

This will generate a response like this:

```
{'access_token': 'Atza|<blah blah blah>', 'refresh_token': 'Atzr|<blah blah blah>', 'token_type': 'bearer', 'expires_in': 3600}
```

Note the access token and the refresh token. In an hour (3600 seconds) the access token will expire. Before that happens, the device should send a refresh request using the refresh token (from the token request) and the client id (same as the auth request). The command will look like this:

```
python3 send_requests.py --request_refresh --refresh_token 'Atzr|<blah blah blah>' --client_id amzn1.application-oa2-client.851d101c41de450280dda151810f1405
```

This will generate a response containing the new refresh and access tokens.