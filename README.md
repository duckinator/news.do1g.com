# news.do1g.com

WIP microblog thing inspired by [Debian micronews](https://micronews.debian.org/).

`./build.py` will generate `_site/`. That's all you need.

# Adding posts manually

The date and time for a post is figured out from the filename.

Posts have a filename of the form `posts/YYYY-MM-DD_HH.MM.SS.html` where:
- `YYYY` is the 4-digit year (e.g. 2023)
- `MM` is the zero-padded month (e.g. `12` or `03`)
- `DD` is the zero-padded date of the month (e.g. `03` or `31`)
- `HH` is the zero-padded 24-hour hour (e.g. `01`, `13`, or `23`)
- `MM` is the zero-padded minute (e.g. `05` or `58`)
- `SS` is the zero-padded second (e.g. `06` or `59`)

## "New Post" bookmarklet

If you want to make posts, make a bookmarklet with the following as the URL:

```
javascript:(function(){date=new Date();y=date.getFullYear();mo=date.getMonth()+1;d=date.getDate();h=date.getHours();mi=date.getMinutes();s=date.getSeconds();location.href='https://github.com/duckinator/news.do1g.com/new/main?filename=posts/'+y+'-'+mo.toString().padStart(2, '0')+'-'+d.toString().padStart(2, '0')+'_'+h.toString().padStart(2, '0')+'.'+mi.toString().padStart(2, '0')+'.'+s.toString().padStart(2, '0')+'.html';})()
```
