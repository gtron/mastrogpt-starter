import re, os, requests as req
#MODEL = "llama3.1:8b"
MODEL = "phi4:14b"

def chat(args, inp):
  host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
  auth = args.get("AUTH", os.getenv("AUTH"))
  url = f"https://{auth}@{host}/api/generate"
  msg = { "model": MODEL, "prompt": inp, "stream": False}
  res = req.post(url, json=msg).json()
  out = res.get("response", "error")
  return  out
 
def extract_fen(out):
  pattern = r"([rnbqkpRNBQKP1-8]+\/){7}[rnbqkpRNBQKP1-8]+"
  fen = None
  m = re.search(pattern, out, re.MULTILINE)
  if m:
    fen = m.group(0)
  return fen

def get_form_for_pieces(_pieces):
  return [
    {
      "name": p,
      "label": f"With a {p}",
      "type": "checkbox",
      "required": True
    } for p in _pieces
  ]

def get_prompt_for_pieces(selected_pieces):
  selected = [k for k,v in selected_pieces.items() if v == 'true']

  out = ''
  if selected.__len__() > 0:
    out = ' with a '

  out = out + ' and a '.join(selected)
  return out 
 

def puzzle(args):
  out = "If you want to see a chess puzzle, type 'puzzle'. To display a fen position, type 'fen <fen string>'."
  inp = args.get("input", "")
  pieces = ["queen", "rook", "knight", "bishop"]

  res = {'form': get_form_for_pieces(pieces)}
  print("Input:", inp)
  
  if inp == "puzzle":
    inp = "generate a chess puzzle in FEN format"
    out = chat(args, inp)
    fen = extract_fen(out)
    if fen:
       print(fen)
       res['chess'] = fen
    else:
      out = "Bad FEN position."
  elif inp.startswith("fen"):
    fen = extract_fen(inp)
    if fen:
       out = "Here you go."
       res['chess'] = fen
  elif inp != "":
    inp = "generate a chess puzzle in FEN format" +  get_prompt_for_pieces(inp['form'])
    print("get_prompt_for_pieces response:",inp)
    
    out = chat(args, inp)
    fen = extract_fen(out)
    print(out, fen)
    if fen:
      res['chess'] = fen
  
  
  res["output"] = out
  return res
