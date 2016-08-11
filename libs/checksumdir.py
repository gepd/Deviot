def dirhash(directory, verbose=0):
  import hashlib, os
  SHAhash = hashlib.md5()
  if not os.path.exists (directory):
    return -1

  try:
    for root, dirs, files in os.walk(directory):
      for names in files:
        if verbose == 1:
            print (b'Hashing', names)
        filepath = os.path.join(root,names)
        with open(filepath, 'rb') as f1:
            while True:
                buf = f1.read(4096)
                if not buf : break
                SHAhash.update(buf)
                SHAhash.hexdigest()           
  except:
    import traceback
    # Print the stack traceback
    traceback.print_exc()
    return -2
    
  return SHAhash.hexdigest()


 