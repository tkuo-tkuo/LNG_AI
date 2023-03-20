# LNG_AI
Automatically generate LNG-like contents based on LNG streaming data

# Non-Technical
- [ ] Get buy-in with LNG members
- [ ] Select & add appropriate license
- [ ] Include overall design chart
- [ ] Include references

# Technical 

## Setup  
- [x] Support conda environment reconstruction

Create your environment by conda
```bash
$ conda env create -f environment.yml
$ conda activate lng_ai
```

Create `.env` and place your keys within like
```bash
export yt_api_key=...
export OPENAI_API_KEY=...
```

## Data Collection & Parsing 
- [x] Download audio files with its original video informations (e.g., title, URL, and publish date)
- [x] Transcribe based on audio files (e.g., Whisper), see more details in [candidates evaluation](transcribe_candidates.md)
- [ ] Convert transcript into prompt/completion JSONL training dataset ([OpenAI dataset preparation](https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset))

Download audio files

```bash
$ python3 download_audio_files.py 
```
Results will be stored in tables with two formats supported, default paths are `audio_infos.md` and `audio_infos.csv`

Transcribe audio files

```bash
$ python3 transcribe_audio_files.py 
```

## Model Training
- [x] Select & download suitable LLM (fine-tuned [Babbage model](https://openai.com/pricing) by OpenAI)
- [ ] Fine-tune by LNG data
- [ ] Manually verify results & gradually improve

## Provide user-friendly UI for public
- [ ] Developer & construct website locally
- [ ] Deploy on cloud
- [ ] Address performance issue if any 