# DumpRequests
Simple stupid class for auto patching the python requests library to dump all requests and responses, for debug purposes.

This is a simple class `DumpRequests` that dynamically patched the popular python requests module to dump all requests and responses. It does it by setting up dynamic hooks for every HTTP method (GET, POST, DELETE, OPTIONS, etc) and it also patches the `Sessions` class. This comes very handy when doing extensive debug sessions and one needs to review all ongoing HTTP traffic generated from requests calls.


# How to use
```
dr = DumpRequests()
print(f"[-] DumpRequests working dir is {dr.working_dir} (is currently patched: {dr.is_requests_debug_already_patched})")
# .. now we need to hyper debug and dump all HTTP requests and responses.
#   let's patch - set up hooks to dump all requests HTTP traffic
dr.patch()
requests.get("https://google.com")
requests.post("http://google.com",data={"a":"b"})

# .. later on you can also unpatch
dr.unpatch()
```

# Demo

![tmpvxo1g5zk_and_iterm](https://user-images.githubusercontent.com/519424/194776786-def6f532-97f6-4702-b257-aaa815f3bd57.png)

![image](https://user-images.githubusercontent.com/519424/194776908-1ff90a8d-0942-490f-8a56-93a1f5209dd5.png)

