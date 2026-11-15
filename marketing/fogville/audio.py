import numpy as np, wave
SR=44100; DUR=27.6; n=int(SR*DUR); t=np.arange(n)/SR
mix=np.zeros(n)
bpm=118; beat=60/bpm
def note(f): return 440*2**((f-69)/12)
chords=[[60,64,67],[55,59,62],[57,60,64],[53,57,60]]  # C G Am F
def add(sig,start):
    i=int(start*SR); j=min(n,i+len(sig)); 
    if i<n: mix[i:j]+=sig[:j-i]
# pluck arp (8ths)
step=beat/2; k=0; tt=0.0
while tt<DUR:
    bar=int(tt/(beat*4))%4; ch=chords[bar]
    m=ch[[0,1,2,1,0,2,1,2][k%8]]+12
    L=int(SR*0.35); x=np.arange(L)/SR
    env=np.exp(-x*9)
    s=(np.sin(2*np.pi*note(m)*x)+0.3*np.sin(2*np.pi*note(m)*2*x))*env*0.16
    add(s,tt); k+=1; tt+=step
# pad + bass per bar
for b in range(int(DUR/(beat*4))+1):
    st=b*beat*4; ch=chords[b%4]; L=int(SR*beat*4); x=np.arange(L)/SR
    env=np.minimum(1,x/0.3)*np.minimum(1,(beat*4-x)/0.3)
    pad=sum(np.sin(2*np.pi*note(m)*x)+0.5*np.sin(2*np.pi*note(m)*1.003*x) for m in ch)*env*0.035
    bass=np.sin(2*np.pi*note(ch[0]-24)*x)*env*0.12
    add(pad+bass,st)
# soft kick on beats
kt=0.0
while kt<DUR:
    L=int(SR*0.25); x=np.arange(L)/SR
    f=50+80*np.exp(-x*30); ph=2*np.pi*np.cumsum(f)/SR
    add(np.sin(ph)*np.exp(-x*14)*0.35,kt); kt+=beat
# whisper section: duck music
duck=np.ones(n); a=int(22.6*SR); duck[a:]=np.linspace(1,0.35,n-a)
# fade in/out
duck*=np.minimum(1,t/0.3)*np.minimum(1,(DUR-t)/1.2)
mix*=duck
# sfx
rng=np.random.default_rng(1)
def pop(start,pitch=900,vol=0.35):
    L=int(SR*0.09); x=np.arange(L)/SR
    f=pitch*np.exp(-x*20)+200; ph=2*np.pi*np.cumsum(f)/SR
    add(np.sin(ph)*np.exp(-x*45)*vol,start)
def whoosh(start,dur=0.45,vol=0.25):
    L=int(SR*dur); x=np.arange(L)/SR
    nz=rng.standard_normal(L); 
    # simple band via moving average difference
    lo=np.convolve(nz,np.ones(30)/30,'same'); s=lo
    env=np.sin(np.pi*x/dur)**2
    add(s*env*vol*3,start)
for c in [0.0,3.05,5.15,6.05,7.35,8.25,9.55,11.68,13.15,14.05,16.15,19.18,20.17,22.72,25.03]: pop(c,1100,0.22)
for c in [2.95,3.1,3.25,9.7,10.45,11.2,13.25,14.1,16.5,17.5,18.3,19.3,19.55,19.75,19.95,20.5,20.95,21.45,21.95,23.1]: pop(c,700,0.3)
for w in [2.7,5.0,7.2,9.4,13.0,16.0,19.0,22.6]: whoosh(w)
# thunder
L=int(SR*1.4); x=np.arange(L)/SR; nz=np.convolve(rng.standard_normal(L),np.ones(200)/200,'same')
add(nz*np.exp(-x*2.5)*2.2,17.85)
mix=np.clip(mix,-1,1)
with wave.open('music.wav','w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32000).astype(np.int16).tobytes())
print('ok', mix.max())
