import json
import os
import requests
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
import logging
log = logging.getLogger("")

def letstalksign_authenticate(request):
    # Extract the URL from the query parameters
    url = "https://lts.lb.gcloud.letstalksign.org/authenticate"
    token_filename_append_str = ""

    host = request.get_host()

    print("request came from host: ", host)

    if (host.startswith("localhost") or host.startswith("127.0.0.1")):
        url = "http://localhost:3000/authenticate"
        # Determine the token file name based on the host name
        token_filename_append_str = "-local"
    
    # Validate the URL
    if not url or not requests.utils.urlparse(url).scheme:
        return HttpResponseBadRequest('<ERROR> Invalid or missing URL parameter. Please provide a valid URL.')
    
    # token_file_name = "token-lms" + token_filename_append_str + ".json"

    # # Check if the token file exists
    # if not os.path.exists(token_file_name):
    #     return JsonResponse({
    #         "error": f"<ERROR> Token file missing!!!...CANNOT PROCEED...{token_file_name}",
    #         "message": "EXITING...Token file missing!!!..."
    #     }, status=500)
    
    # # Read the token file
    # try:
    #     with open(token_file_name, "r") as file:
    #         token_data = json.load(file)
    # except Exception as e:
    #     return JsonResponse({
    #         "error": "Unable to open or read the token file.",
    #         "details": str(e)
    #     }, status=500)
    
    # Prepare the data to send in the POST request
    # data_to_send = {
    #     "customer_id": token_data.get("customer_id"),
    #     "api_token": token_data.get("api_token")
    # }
    lts_customer_id = settings.FEATURES.get('LTS_CUSTOMER_ID', '')
    lts_api_token = settings.FEATURES.get('LTS_API_TOKEN', '')

    data_to_send = {
        "customer_id": lts_customer_id,
        "api_token": lts_api_token
    }
    log.info("Let's talk crendential {}".format(data_to_send))
    # Make the POST request
    try:
        response = requests.post(url, data=data_to_send, headers={"Content-Type": "application/x-www-form-urlencoded"})
    except requests.RequestException as e:
        return JsonResponse({
            "error": "Failed to make the API call.",
            "details": str(e)
        }, status=500)
    
    # Handle the response
    if response.status_code != 200:
        return JsonResponse({
            "error": "Authentication Failed",
            "status_code": response.status_code,
            "message": "Unauthorized access - invalid credentials"
        }, status=response.status_code)
    
    try:
        res_data = response.json()
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "Failed to parse the response as JSON.",
            "response_text": response.text
        }, status=500)
    
    # Add headers to the response
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "Origin, X-Requested-With, Content-Type, Accept",
        "Authentication": res_data.get("token", "")
    }
    
    # Return the response
    return JsonResponse(res_data, headers=response_headers)

