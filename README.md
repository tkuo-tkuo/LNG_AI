# LNG_AI
Automatically generate LNG-like contents based on LNG streaming data

# Non-Technical
- [ ] Get buy-in with LNG members
- [ ] Select & add appropriate license
- [ ] Include overall design chart
- [ ] Include references

# Technical 

1. Data Collection & Parsing 
- [x] Download audio files with its original video informations (e.g., title, URL, and publish date)

*Pre-requisite: put your Google Cloud Youtube API in `download_audio_files.py`*
```bash
$ python3 download_audio_files.py 
```
Results will be stored in tables with two formats supported, default paths are `audio_infos.md` and `audio_infos.csv`

- [ ] Generate transcripts based on audio files (e.g., 雅婷逐字稿)

2. Model Training
- [ ] Select & download suitable LLM
- [ ] Fine-tune by LNG data
- [ ] Manually verify results & gradually improve

3. Provide user-friendly UI for public
- [ ] Developer & construct website locally
- [ ] Deploy on cloud
- [ ] Address performance issue if any 
- [ ] Make this repository re-producible (e.g., docker)