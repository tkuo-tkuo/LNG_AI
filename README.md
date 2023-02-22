# LNG_AI
Automatically generate LNG-like contents based on LNG streaming data

# Non-Technical
- [ ] Get buy-in with LNG members
- [ ] Select & add appropriate license

# Technical 

1. Data Collection & Parsing 
- [x] Grab latest LNG video informations (e.g., URL and publish date)  

*Pre-requisite: put your Google Cloud Youtube API in `obtain_latest_video_infos.py`*
```bash
$ python3 obtain_latest_video_infos.py 
```
Results will be stored in tables with two formats supported, default paths are `latest_video_infos.md` and `latest_video_infos.csv`

- [ ] Download audio files
- [ ] Generate transcripts based on audio files

2. Model Training
- [ ] Select & download suitable LLM
- [ ] Fine-tune by LNG data
- [ ] Manually verify results & gradually improve

3. Provide user-friendly UI for public
- [ ] Developer & construct website locally
- [ ] Deploy on cloud
- [ ] Address performance issue if any 
