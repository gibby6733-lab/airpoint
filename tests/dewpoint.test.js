function dewPointC(t,rh){const a=17.62,b=243.12;const gamma=Math.log(rh/100)+(a*t)/(b+t);return (b*gamma)/(a-gamma)}
function close(a,b,t=.15){if(Math.abs(a-b)>t)throw new Error(`Expected ${b}, got ${a}`)}
const cases=[[25,60,16.7],[20,50,9.3],[30,70,23.9],[0,80,-2.9],[40,50,27.6]]
for(const [t,rh,expected] of cases){close(dewPointC(t,rh),expected);console.log(`PASS ${t}C/${rh}%`)}
for(let t=-20;t<=50;t+=5){let prev=-999;for(let rh=10;rh<=100;rh+=10){const d=dewPointC(t,rh);if(d<prev)throw new Error("Monotonicity failure");prev=d}}
console.log("PASS monotonic humidity tests")
console.log("ALL TESTS PASS")