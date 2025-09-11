import onnxruntime as ort

# 1. Create a SessionOptions object
so = ort.SessionOptions()

# 2. Set the log severity level
# 0 = Verbose, 1 = Info, 2 = Warning, 3 = Error
so.log_severity_level = 0 

print(ort.get_available_providers())

