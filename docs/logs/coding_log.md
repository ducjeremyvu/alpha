# Coding Log

## 2026-01-21

### Daily next-candle behavior (US500)

Ran `scripts/experiments/daily_next_candle_behavior.py` over ~4,683 daily candles.
The next candle skews green in both cases (green→green 53.6%, red→green 56.5%),
but the effect is tiny. Chi‑square shows weak dependence (p=0.210 for 3x3;
p=0.051 for green/red only) with very small effect size (Cramér’s V ≈ 0.03).
Conclusion: mild bullish bias in the sample, but prior candle alone has limited
predictive power.

## 2025-11-15 Summary everything done 

### api layer
done 
### frontend layer 
done, but still need to familiarize with javascript and html

### More ideas 
#### Caching 
need to do 
### new page 


### understanding javascript 

so in html, define html elements
html doc has <style> in <head>


## 2025-11-14

### ruff package

I've added ruff to the environment 

It's a package that shows how styles are off certain style guides 

```
uv run ruff check . --exclude "*.ipynb"  
```

will only scan files, no jupyter notebooks 


### refactoring

so i did some refactoring and 

### git commit format 

i wanted some unformity when it comes to git commits, so i can instantly see what was done etc.
usually i was adding everything , then adding some commit message, but it wasnt clear enough, so i wanted some framework. 

with the help of gpt, i could find something that comes with little overhead and forces good practices in communicating commits 
