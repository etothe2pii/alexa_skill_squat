import requests
from argparse import ArgumentParser


'''
Most of this is based off of instructions in Authorize an AVS Device Through Code-Based Linking (CBL)
https://developer.amazon.com/en-US/docs/alexa/alexa-voice-service/authorize-cbl.html

'''

'''
Start here! This lets you get the code based linkage codes. Next up is requesting device tokens!

The first time a device is used, the user needs to go to the URL that the auth request (verification_uri) gives them (as of writing, thats https://amazon.com/us/code) and enter the user code. 
If all goes well, the device should be registered. If you get a page with a vague error message (something like "we're sorry, we're not sure what went wrong. We're working on the problem right now!")
it probably means you used the wrong product id. (This message also appears if the post request is malformed. Be forewarned.)

Quick tip on the requests.Response objects: most of the time calling .json() on them (which effectively converts them into a dict) makes them much easier to work with.

Just fyi, client id and product id are set/generated on your avs developer console. (https://developer.amazon.com/alexa/console/avs/products)
args:
    client_id: Get this from your device's security profile (use Other devices and platforms).
    product_id: Get this from your device's information tab (You set this when setting up the device!)
    device_serial_number: Just put something random. 12345 should work for most simple cases.
'''
def post_auth_request(client_id, product_id, device_serial_number = "12345") -> requests.Response:
    url = "https://api.amazon.com/auth/O2/create/codepair"

    scope = {"alexa:all": {"productID": product_id, "productInstanceAttributes": {"deviceSerialNumber": device_serial_number}}}

    j = {
            "response_type": "device_code",
            "client_id": client_id,
            "scope": "alexa:all",
            "scope_data" : scope,
         }
    
    return requests.post(url, json = j)

'''
This gets you the access and refresh tokens. These seem to need to be renewed each hour.

args: 
    device_code: From the auth request
    user_code: Also from the auth request

'''

def request_device_tokens(device_code, user_code)  -> requests.Response:

    url = "https://api.amazon.com/auth/O2/token"

    j = {
            "grant_type":"device_code",
            "device_code": device_code,
            "user_code": user_code,
         }
    
    return requests.post(url, json=j)

def request_token_refresh(refresh_token, client_id) -> requests.Response:

    url = "https://api.amazon.com/auth/O2/token"

    j = {
            "grant_type":"refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
         }
    
    return requests.post(url, json=j)    

'''
A simple verification workflow. Hopefully, if you type in the correct client_id and product_id (same params as post_auth_request) everything should work!
'''

def setup_new_device(client_id, product_id, device_serial_number = "12345"):
    auth = post_auth_request(client_id, product_id, device_serial_number=device_serial_number).json()

    print(f"Please visit {auth['verification_uri']} and when prompted enter the verification code {auth['user_code']}")
    print(f"Code expires in {auth['expires_in']}.")
    input("Press enter when finished . . .")

    print("Retrieving device tokens")

    tokens = request_device_tokens(auth["device_code"], auth["user_code"]).json()

    print(f"Access Token: {tokens['access_token']}")
    print(f"Refresh Token: {tokens['refresh_token']}")
    print(f"Token expires in {tokens['expires_in']} seconds.")

    return tokens['access_token'], tokens['refresh_token'], tokens['expires_in']




if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("--setup_device", action="store_true", help="Flag to set up new device.")
    parser.add_argument("--auth_request", "-a", action="store_true", help="Flag to send auth request")
    parser.add_argument("--client_id", default="amzn1.application-oa2-client.acf713904d2e4145aed1658e8323313a", help = "Set client id")
    parser.add_argument("--product_id", default="TDevice", help="Set product id")
    parser.add_argument("--serial_number", default = "12345", help="set device serial number")

    parser.add_argument("--request_tokens", "-t", action="store_true", help="Flag to send device token request")
    parser.add_argument("--device_code", default = "361acb92-dc4c-4d40-90e7-ad4d98968a4c", help = "Device code from auth_request")
    parser.add_argument("--user_code", default="F44WJN", help = "User code from auth request")


    parser.add_argument("--request_refresh", "-r", action="store_true", help="Flag to refresh the access and refresh tokens request")
    parser.add_argument("--refresh_token", default = "", help = "refresh token from request device tokens")

    
    args = parser.parse_args()


    if args.auth_request:

        x = post_auth_request(args.client_id, args.product_id, device_serial_number=args.serial_number)

        print(x.text)

    if args.request_tokens:
        x = request_device_tokens(args.device_code, args.user_code)
        print(x.text)

    if args.setup_device:
        x = setup_new_device(args.client_id, args.product_id, device_serial_number=args.serial_number)

        print(x)

    if args.request_refresh:
        x = request_token_refresh(args.refresh_token, args.client_id)
