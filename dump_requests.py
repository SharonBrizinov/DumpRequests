import os
import tempfile
import time
from urllib.parse import urlparse
import requests


_REQUESTS_PATCH_HTTP_METHODS = ['get', 'options', 'head', 'post', 'put', 'patch', 'delete']
_REQUESTS_PATCH_ORIGINAL_REQUESTS_FUNCS = dict([(method_name, getattr(requests, method_name)) for method_name in _REQUESTS_PATCH_HTTP_METHODS])
_REQUESTS_PATCH_ORIGINAL_DEFAULT_SESSION_CLASS = requests.Session
_REQUESTS_PATCH_TEMP_DIR = None

class DumpRequests(object):    

    def __init__(self, output_dir=None):
        global _REQUESTS_PATCH_TEMP_DIR
        _REQUESTS_PATCH_TEMP_DIR = output_dir or tempfile.mkdtemp()
        self.working_dir = _REQUESTS_PATCH_TEMP_DIR
        self.is_requests_debug_already_patched = False
    
    @staticmethod
    def dump_request(response, *args, **kw):
        file_name = str(time.time()) + "_" + urlparse(response.url).netloc + ".req.res.txt"
        file_path = os.path.join(_REQUESTS_PATCH_TEMP_DIR, file_name)
        list_responses = response.history or [response]
        with open(file_path, "wb") as f:
            # Dump HTTP request and response
            for res in list_responses:
                ######### REQUEST #######
                f.write(f"{res.request.method} {res.url}\n".encode())

                # request headers
                for header_key, header_val in res.request.headers.items():
                    f.write(f"{header_key}: {header_val}\n".encode())

                f.write("\n".encode())

                # request body
                req_body = res.request.body
                if req_body:
                    if type(req_body) == str:
                        f.write(f"{req_body}".encode())
                    elif  type(req_body) == bytes:
                        f.write(req_body)
                    else:
                        # unknown
                        pass
                f.write("\n".encode())
                f.write("\n".encode())

                ######### RESPONSE #######
                f.write(f"{res.status_code} {res.reason}\n".encode())

                # response headers
                for header_key, header_val in res.headers.items():
                    f.write(f"{header_key}: {header_val}\n".encode())

                f.write("\n".encode())

                # response body
                res_body = res.content
                if res_body:
                    f.write(res_body)

                f.write("\n".encode())
                f.write("--------------------------------------\n".encode())
                f.write("--------------------------------------\n".encode())
                f.write("--------------------------------------\n".encode())
                f.write("--------------------------------------\n".encode())
                f.write("--------------------------------------\n".encode())
                f.write("\n".encode())
                f.write("\n".encode())

    @staticmethod
    def hook_function(method_name):
        def inner(*args, **kw):
            func = _REQUESTS_PATCH_ORIGINAL_REQUESTS_FUNCS.get(method_name)
            hooks = {}
            # maybe kwargs has hooks already
            if "hooks" in kw:
                hooks = kw.pop("hooks")
            hooks["response"] = DumpRequests.dump_request
            return func(*args, hooks=hooks, **kw)
        return inner


    class MyPatchedSession(_REQUESTS_PATCH_ORIGINAL_DEFAULT_SESSION_CLASS):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._patch_hooks()

        def _patch_hooks(self):
            if "response" in self.hooks:
                if type(self.hooks["response"]) is list:
                    self.hooks["response"].append(DumpRequests.dump_request)
                else:
                    current_hook = self.hooks["response"]
                    self.hooks["response"] = [current_hook, DumpRequests.dump_request]
            else:
                self.hooks["response"] = [DumpRequests.dump_request]


    def patch(self):
        self.is_requests_debug_already_patched = True
        requests.Session = DumpRequests.MyPatchedSession
        for method_name in _REQUESTS_PATCH_HTTP_METHODS:
            setattr(requests, method_name, DumpRequests.hook_function(method_name))

    def unpatch(self):
        self.is_requests_debug_already_patched = False
        requests.Session = _REQUESTS_PATCH_ORIGINAL_DEFAULT_SESSION_CLASS
        for method_name in _REQUESTS_PATCH_ORIGINAL_REQUESTS_FUNCS.keys():
            func = _REQUESTS_PATCH_ORIGINAL_REQUESTS_FUNCS[method_name]
            setattr(requests, method_name, func)



def main():
    print(f"[-] Testing DumpRequests class for dynamic patching of requests")
    dr = DumpRequests()
    print(f"[-] DumpRequests working dir is {dr.working_dir} (is currently patched: {dr.is_requests_debug_already_patched})")

    print(f"[-] DumpRequests - do patch")
    dr.patch()
    print(f"[-] DumpRequests - send requests to google (GET, POST) (is currently patched: {dr.is_requests_debug_already_patched})")
    requests.get("https://google.com")
    requests.post("http://google.com",data={"a":"b"})

    print(f"[-] DumpRequests - do unpatch")
    dr.unpatch()
    print(f"[-] DumpRequests - send requests to apple (GET, POST (is currently patched: {dr.is_requests_debug_already_patched})")
    requests.get("https://apple.com")
    requests.post("http://apple.com",data={"a":"b"})

    print(f"[-] DumpRequests - do patch")
    dr.patch()
    print(f"[-] DumpRequests - send session requests to microsoft (GET, POST) (is currently patched: {dr.is_requests_debug_already_patched})")
    s1 = requests.Session()
    s1.get("https://microsoft.com")
    s1.post("http://microsoft.com",data={"a":"b"})

if __name__ == "__main__":
    main()
