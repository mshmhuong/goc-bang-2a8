import asyncio, json, os, urllib.request, urllib.parse
import edge_tts
os.makedirs('out/a', exist_ok=True); os.makedirs('out/v', exist_ok=True); os.makedirs('out/i', exist_ok=True)
T = json.load(open('tools/texts.json'))
async def g(text, voice, rate, path):
    for k in range(4):
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(path); return
        except Exception as e:
            print('retry', text, e); await asyncio.sleep(3)
async def main():
    for i, (t, slow) in enumerate(T['items']):
        await g(t, T['voice'], '-30%' if slow else T['rate'], f'out/a/{i:02d}.mp3')
    for v in T['probe']:
        await g('farm', v, T['rate'], f'out/v/{v}.mp3')
asyncio.run(main())
UA = {'User-Agent': 'GocBang2A8/1.0 (classroom flashcards; github.com/mshmhuong)'}
for name, q in T['img'].items():
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action':'query','format':'json','generator':'search','gsrsearch':'filetype:bitmap '+q,'gsrnamespace':6,'gsrlimit':8,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':800})
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        meta = []
        for j, p in enumerate(sorted(d.get('query', {}).get('pages', {}).values(), key=lambda p: p.get('index', 0))):
            ii = p['imageinfo'][0]; u = ii.get('thumburl') or ii['url']
            fn = f'out/i/{name}_{j}.jpg'
            open(fn, 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read())
            em = ii.get('extmetadata', {})
            meta.append({'f': fn, 'title': p['title'], 'lic': em.get('LicenseShortName', {}).get('value'), 'artist': em.get('Artist', {}).get('value', '')[:200]})
        json.dump(meta, open(f'out/i/{name}.json', 'w'), ensure_ascii=False, indent=1)
    except Exception as e:
        print('img fail', name, e)
