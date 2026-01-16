// deno:https://esm.sh/@codemirror/state@0.20.1/denonext/state.mjs
var m = class s {
  constructor() {
  }
  lineAt(e) {
    if (e < 0 || e > this.length) throw new RangeError(`Invalid position ${e} in document of length ${this.length}`);
    return this.lineInner(e, false, 1, 0);
  }
  line(e) {
    if (e < 1 || e > this.lines) throw new RangeError(`Invalid line number ${e} in ${this.lines}-line document`);
    return this.lineInner(e, true, 1, 0);
  }
  replace(e, t3, n11) {
    let i2 = [];
    return this.decompose(0, e, i2, 2), n11.length && n11.decompose(0, n11.length, i2, 3), this.decompose(t3, this.length, i2, 1), N.from(i2, this.length - (t3 - e) + n11.length);
  }
  append(e) {
    return this.replace(this.length, this.length, e);
  }
  slice(e, t3 = this.length) {
    let n11 = [];
    return this.decompose(e, t3, n11, 0), N.from(n11, t3 - e);
  }
  eq(e) {
    if (e == this) return true;
    if (e.length != this.length || e.lines != this.lines) return false;
    let t3 = this.scanIdentical(e, 1), n11 = this.length - this.scanIdentical(e, -1), i2 = new B(this), r2 = new B(e);
    for (let l9 = t3, h = t3; ; ) {
      if (i2.next(l9), r2.next(l9), l9 = 0, i2.lineBreak != r2.lineBreak || i2.done != r2.done || i2.value != r2.value) return false;
      if (h += i2.value.length, i2.done || h >= n11) return true;
    }
  }
  iter(e = 1) {
    return new B(this, e);
  }
  iterRange(e, t3 = this.length) {
    return new X(this, e, t3);
  }
  iterLines(e, t3) {
    let n11;
    if (e == null) n11 = this.iter();
    else {
      t3 == null && (t3 = this.lines + 1);
      let i2 = this.line(e).from;
      n11 = this.iterRange(i2, Math.max(i2, t3 == this.lines + 1 ? this.length : t3 <= 1 ? 0 : this.line(t3 - 1).to));
    }
    return new Y(n11);
  }
  toString() {
    return this.sliceString(0);
  }
  toJSON() {
    let e = [];
    return this.flatten(e), e;
  }
  static of(e) {
    if (e.length == 0) throw new RangeError("A document must have at least one line");
    return e.length == 1 && !e[0] ? s.empty : e.length <= 32 ? new k(e) : N.from(k.split(e, []));
  }
};
var k = class s2 extends m {
  constructor(e, t3 = je(e)) {
    super(), this.text = e, this.length = t3;
  }
  get lines() {
    return this.text.length;
  }
  get children() {
    return null;
  }
  lineInner(e, t3, n11, i2) {
    for (let r2 = 0; ; r2++) {
      let l9 = this.text[r2], h = i2 + l9.length;
      if ((t3 ? n11 : h) >= e) return new ae(i2, h, n11, l9);
      i2 = h + 1, n11++;
    }
  }
  decompose(e, t3, n11, i2) {
    let r2 = e <= 0 && t3 >= this.length ? this : new s2(Ie(this.text, e, t3), Math.min(t3, this.length) - Math.max(0, e));
    if (i2 & 1) {
      let l9 = n11.pop(), h = Q(r2.text, l9.text.slice(), 0, r2.length);
      if (h.length <= 32) n11.push(new s2(h, l9.length + r2.length));
      else {
        let o3 = h.length >> 1;
        n11.push(new s2(h.slice(0, o3)), new s2(h.slice(o3)));
      }
    } else n11.push(r2);
  }
  replace(e, t3, n11) {
    if (!(n11 instanceof s2)) return super.replace(e, t3, n11);
    let i2 = Q(this.text, Q(n11.text, Ie(this.text, 0, e)), t3), r2 = this.length + n11.length - (t3 - e);
    return i2.length <= 32 ? new s2(i2, r2) : N.from(s2.split(i2, []), r2);
  }
  sliceString(e, t3 = this.length, n11 = `
`) {
    let i2 = "";
    for (let r2 = 0, l9 = 0; r2 <= t3 && l9 < this.text.length; l9++) {
      let h = this.text[l9], o3 = r2 + h.length;
      r2 > e && l9 && (i2 += n11), e < o3 && t3 > r2 && (i2 += h.slice(Math.max(0, e - r2), t3 - r2)), r2 = o3 + 1;
    }
    return i2;
  }
  flatten(e) {
    for (let t3 of this.text) e.push(t3);
  }
  scanIdentical() {
    return 0;
  }
  static split(e, t3) {
    let n11 = [], i2 = -1;
    for (let r2 of e) n11.push(r2), i2 += r2.length + 1, n11.length == 32 && (t3.push(new s2(n11, i2)), n11 = [], i2 = -1);
    return i2 > -1 && t3.push(new s2(n11, i2)), t3;
  }
};
var N = class s3 extends m {
  constructor(e, t3) {
    super(), this.children = e, this.length = t3, this.lines = 0;
    for (let n11 of e) this.lines += n11.lines;
  }
  lineInner(e, t3, n11, i2) {
    for (let r2 = 0; ; r2++) {
      let l9 = this.children[r2], h = i2 + l9.length, o3 = n11 + l9.lines - 1;
      if ((t3 ? o3 : h) >= e) return l9.lineInner(e, t3, n11, i2);
      i2 = h + 1, n11 = o3 + 1;
    }
  }
  decompose(e, t3, n11, i2) {
    for (let r2 = 0, l9 = 0; l9 <= t3 && r2 < this.children.length; r2++) {
      let h = this.children[r2], o3 = l9 + h.length;
      if (e <= o3 && t3 >= l9) {
        let a2 = i2 & ((l9 <= e ? 1 : 0) | (o3 >= t3 ? 2 : 0));
        l9 >= e && o3 <= t3 && !a2 ? n11.push(h) : h.decompose(e - l9, t3 - l9, n11, a2);
      }
      l9 = o3 + 1;
    }
  }
  replace(e, t3, n11) {
    if (n11.lines < this.lines) for (let i2 = 0, r2 = 0; i2 < this.children.length; i2++) {
      let l9 = this.children[i2], h = r2 + l9.length;
      if (e >= r2 && t3 <= h) {
        let o3 = l9.replace(e - r2, t3 - r2, n11), a2 = this.lines - l9.lines + o3.lines;
        if (o3.lines < a2 >> 4 && o3.lines > a2 >> 6) {
          let f = this.children.slice();
          return f[i2] = o3, new s3(f, this.length - (t3 - e) + n11.length);
        }
        return super.replace(r2, h, o3);
      }
      r2 = h + 1;
    }
    return super.replace(e, t3, n11);
  }
  sliceString(e, t3 = this.length, n11 = `
`) {
    let i2 = "";
    for (let r2 = 0, l9 = 0; r2 < this.children.length && l9 <= t3; r2++) {
      let h = this.children[r2], o3 = l9 + h.length;
      l9 > e && r2 && (i2 += n11), e < o3 && t3 > l9 && (i2 += h.sliceString(e - l9, t3 - l9, n11)), l9 = o3 + 1;
    }
    return i2;
  }
  flatten(e) {
    for (let t3 of this.children) t3.flatten(e);
  }
  scanIdentical(e, t3) {
    if (!(e instanceof s3)) return 0;
    let n11 = 0, [i2, r2, l9, h] = t3 > 0 ? [
      0,
      0,
      this.children.length,
      e.children.length
    ] : [
      this.children.length - 1,
      e.children.length - 1,
      -1,
      -1
    ];
    for (; ; i2 += t3, r2 += t3) {
      if (i2 == l9 || r2 == h) return n11;
      let o3 = this.children[i2], a2 = e.children[r2];
      if (o3 != a2) return n11 + o3.scanIdentical(a2, t3);
      n11 += o3.length + 1;
    }
  }
  static from(e, t3 = e.reduce((n11, i2) => n11 + i2.length + 1, -1)) {
    let n11 = 0;
    for (let d of e) n11 += d.lines;
    if (n11 < 32) {
      let d = [];
      for (let g3 of e) g3.flatten(d);
      return new k(d, t3);
    }
    let i2 = Math.max(32, n11 >> 5), r2 = i2 << 1, l9 = i2 >> 1, h = [], o3 = 0, a2 = -1, f = [];
    function u2(d) {
      let g3;
      if (d.lines > r2 && d instanceof s3) for (let A6 of d.children) u2(A6);
      else d.lines > l9 && (o3 > l9 || !o3) ? (c3(), h.push(d)) : d instanceof k && o3 && (g3 = f[f.length - 1]) instanceof k && d.lines + g3.lines <= 32 ? (o3 += d.lines, a2 += d.length + 1, f[f.length - 1] = new k(g3.text.concat(d.text), g3.length + 1 + d.length)) : (o3 + d.lines > i2 && c3(), o3 += d.lines, a2 += d.length + 1, f.push(d));
    }
    function c3() {
      o3 != 0 && (h.push(f.length == 1 ? f[0] : s3.from(f, a2)), a2 = -1, o3 = f.length = 0);
    }
    for (let d of e) u2(d);
    return c3(), h.length == 1 ? h[0] : new s3(h, t3);
  }
};
m.empty = new k([
  ""
], 0);
function je(s45) {
  let e = -1;
  for (let t3 of s45) e += t3.length + 1;
  return e;
}
function Q(s45, e, t3 = 0, n11 = 1e9) {
  for (let i2 = 0, r2 = 0, l9 = true; r2 < s45.length && i2 <= n11; r2++) {
    let h = s45[r2], o3 = i2 + h.length;
    o3 >= t3 && (o3 > n11 && (h = h.slice(0, n11 - i2)), i2 < t3 && (h = h.slice(t3 - i2)), l9 ? (e[e.length - 1] += h, l9 = false) : e.push(h)), i2 = o3 + 1;
  }
  return e;
}
function Ie(s45, e, t3) {
  return Q(s45, [
    ""
  ], e, t3);
}
var B = class {
  constructor(e, t3 = 1) {
    this.dir = t3, this.done = false, this.lineBreak = false, this.value = "", this.nodes = [
      e
    ], this.offsets = [
      t3 > 0 ? 1 : (e instanceof k ? e.text.length : e.children.length) << 1
    ];
  }
  nextInner(e, t3) {
    for (this.done = this.lineBreak = false; ; ) {
      let n11 = this.nodes.length - 1, i2 = this.nodes[n11], r2 = this.offsets[n11], l9 = r2 >> 1, h = i2 instanceof k ? i2.text.length : i2.children.length;
      if (l9 == (t3 > 0 ? h : 0)) {
        if (n11 == 0) return this.done = true, this.value = "", this;
        t3 > 0 && this.offsets[n11 - 1]++, this.nodes.pop(), this.offsets.pop();
      } else if ((r2 & 1) == (t3 > 0 ? 0 : 1)) {
        if (this.offsets[n11] += t3, e == 0) return this.lineBreak = true, this.value = `
`, this;
        e--;
      } else if (i2 instanceof k) {
        let o3 = i2.text[l9 + (t3 < 0 ? -1 : 0)];
        if (this.offsets[n11] += t3, o3.length > Math.max(0, e)) return this.value = e == 0 ? o3 : t3 > 0 ? o3.slice(e) : o3.slice(0, o3.length - e), this;
        e -= o3.length;
      } else {
        let o3 = i2.children[l9 + (t3 < 0 ? -1 : 0)];
        e > o3.length ? (e -= o3.length, this.offsets[n11] += t3) : (t3 < 0 && this.offsets[n11]--, this.nodes.push(o3), this.offsets.push(t3 > 0 ? 1 : (o3 instanceof k ? o3.text.length : o3.children.length) << 1));
      }
    }
  }
  next(e = 0) {
    return e < 0 && (this.nextInner(-e, -this.dir), e = this.value.length), this.nextInner(e, this.dir);
  }
};
var X = class {
  constructor(e, t3, n11) {
    this.value = "", this.done = false, this.cursor = new B(e, t3 > n11 ? -1 : 1), this.pos = t3 > n11 ? e.length : 0, this.from = Math.min(t3, n11), this.to = Math.max(t3, n11);
  }
  nextInner(e, t3) {
    if (t3 < 0 ? this.pos <= this.from : this.pos >= this.to) return this.value = "", this.done = true, this;
    e += Math.max(0, t3 < 0 ? this.pos - this.to : this.from - this.pos);
    let n11 = t3 < 0 ? this.pos - this.from : this.to - this.pos;
    e > n11 && (e = n11), n11 -= e;
    let { value: i2 } = this.cursor.next(e);
    return this.pos += (i2.length + e) * t3, this.value = i2.length <= n11 ? i2 : t3 < 0 ? i2.slice(i2.length - n11) : i2.slice(0, n11), this.done = !this.value, this;
  }
  next(e = 0) {
    return e < 0 ? e = Math.max(e, this.from - this.pos) : e > 0 && (e = Math.min(e, this.to - this.pos)), this.nextInner(e, this.cursor.dir);
  }
  get lineBreak() {
    return this.cursor.lineBreak && this.value != "";
  }
};
var Y = class {
  constructor(e) {
    this.inner = e, this.afterBreak = true, this.value = "", this.done = false;
  }
  next(e = 0) {
    let { done: t3, lineBreak: n11, value: i2 } = this.inner.next(e);
    return t3 ? (this.done = true, this.value = "") : n11 ? this.afterBreak ? this.value = "" : (this.afterBreak = true, this.next()) : (this.value = i2, this.afterBreak = false), this;
  }
  get lineBreak() {
    return false;
  }
};
typeof Symbol < "u" && (m.prototype[Symbol.iterator] = function() {
  return this.iter();
}, B.prototype[Symbol.iterator] = X.prototype[Symbol.iterator] = Y.prototype[Symbol.iterator] = function() {
  return this;
});
var ae = class {
  constructor(e, t3, n11, i2) {
    this.from = e, this.to = t3, this.number = n11, this.text = i2;
  }
  get length() {
    return this.to - this.from;
  }
};
var D = "lc,34,7n,7,7b,19,,,,2,,2,,,20,b,1c,l,g,,2t,7,2,6,2,2,,4,z,,u,r,2j,b,1m,9,9,,o,4,,9,,3,,5,17,3,3b,f,,w,1j,,,,4,8,4,,3,7,a,2,t,,1m,,,,2,4,8,,9,,a,2,q,,2,2,1l,,4,2,4,2,2,3,3,,u,2,3,,b,2,1l,,4,5,,2,4,,k,2,m,6,,,1m,,,2,,4,8,,7,3,a,2,u,,1n,,,,c,,9,,14,,3,,1l,3,5,3,,4,7,2,b,2,t,,1m,,2,,2,,3,,5,2,7,2,b,2,s,2,1l,2,,,2,4,8,,9,,a,2,t,,20,,4,,2,3,,,8,,29,,2,7,c,8,2q,,2,9,b,6,22,2,r,,,,,,1j,e,,5,,2,5,b,,10,9,,2u,4,,6,,2,2,2,p,2,4,3,g,4,d,,2,2,6,,f,,jj,3,qa,3,t,3,t,2,u,2,1s,2,,7,8,,2,b,9,,19,3,3b,2,y,,3a,3,4,2,9,,6,3,63,2,2,,1m,,,7,,,,,2,8,6,a,2,,1c,h,1r,4,1c,7,,,5,,14,9,c,2,w,4,2,2,,3,1k,,,2,3,,,3,1m,8,2,2,48,3,,d,,7,4,,6,,3,2,5i,1m,,5,ek,,5f,x,2da,3,3x,,2o,w,fe,6,2x,2,n9w,4,,a,w,2,28,2,7k,,3,,4,,p,2,5,,47,2,q,i,d,,12,8,p,b,1a,3,1c,,2,4,2,2,13,,1v,6,2,2,2,2,c,,8,,1b,,1f,,,3,2,2,5,2,,,16,2,8,,6m,,2,,4,,fn4,,kh,g,g,g,a6,2,gt,,6a,,45,5,1ae,3,,2,5,4,14,3,4,,4l,2,fx,4,ar,2,49,b,4w,,1i,f,1k,3,1d,4,2,2,1x,3,10,5,,8,1q,,c,2,1g,9,a,4,2,,2n,3,2,,,2,6,,4g,,3,8,l,2,1l,2,,,,,m,,e,7,3,5,5f,8,2,3,,,n,,29,,2,6,,,2,,,2,,2,6j,,2,4,6,2,,2,r,2,2d,8,2,,,2,2y,,,,2,6,,,2t,3,2,4,,5,77,9,,2,6t,,a,2,,,4,,40,4,2,2,4,,w,a,14,6,2,4,8,,9,6,2,3,1a,d,,2,ba,7,,6,,,2a,m,2,7,,2,,2,3e,6,3,,,2,,7,,,20,2,3,,,,9n,2,f0b,5,1n,7,t4,,1r,4,29,,f5k,2,43q,,,3,4,5,8,8,2,7,u,4,44,3,1iz,1j,4,1e,8,,e,,m,5,,f,11s,7,,h,2,7,,2,,5,79,7,c5,4,15s,7,31,7,240,5,gx7k,2o,3k,6o".split(",").map((s45) => s45 ? parseInt(s45, 36) : 1);
for (let s45 = 1; s45 < D.length; s45++) D[s45] += D[s45 - 1];
function He(s45) {
  for (let e = 1; e < D.length; e += 2) if (D[e] > s45) return D[e - 1] <= s45;
  return false;
}
function Ae(s45) {
  return s45 >= 127462 && s45 <= 127487;
}
var Pe = 8205;
function _(s45, e, t3 = true, n11 = true) {
  return (t3 ? Ce : Ze)(s45, e, n11);
}
function Ce(s45, e, t3) {
  if (e == s45.length) return e;
  e && Me(s45.charCodeAt(e)) && Fe(s45.charCodeAt(e - 1)) && e--;
  let n11 = he(s45, e);
  for (e += be(n11); e < s45.length; ) {
    let i2 = he(s45, e);
    if (n11 == Pe || i2 == Pe || t3 && He(i2)) e += be(i2), n11 = i2;
    else if (Ae(i2)) {
      let r2 = 0, l9 = e - 2;
      for (; l9 >= 0 && Ae(he(s45, l9)); ) r2++, l9 -= 2;
      if (r2 % 2 == 0) break;
      e += 2;
    } else break;
  }
  return e;
}
function Ze(s45, e, t3) {
  for (; e > 0; ) {
    let n11 = Ce(s45, e - 2, t3);
    if (n11 < e) return n11;
    e--;
  }
  return 0;
}
function Me(s45) {
  return s45 >= 56320 && s45 < 57344;
}
function Fe(s45) {
  return s45 >= 55296 && s45 < 56320;
}
function he(s45, e) {
  let t3 = s45.charCodeAt(e);
  if (!Fe(t3) || e + 1 == s45.length) return t3;
  let n11 = s45.charCodeAt(e + 1);
  return Me(n11) ? (t3 - 55296 << 10) + (n11 - 56320) + 65536 : t3;
}
function rt(s45) {
  return s45 <= 65535 ? String.fromCharCode(s45) : (s45 -= 65536, String.fromCharCode((s45 >> 10) + 55296, (s45 & 1023) + 56320));
}
function be(s45) {
  return s45 < 65536 ? 1 : 2;
}
var fe = /\r\n?|\n/;
var b = function(s45) {
  return s45[s45.Simple = 0] = "Simple", s45[s45.TrackDel = 1] = "TrackDel", s45[s45.TrackBefore = 2] = "TrackBefore", s45[s45.TrackAfter = 3] = "TrackAfter", s45;
}(b || (b = {}));
var C = class s4 {
  constructor(e) {
    this.sections = e;
  }
  get length() {
    let e = 0;
    for (let t3 = 0; t3 < this.sections.length; t3 += 2) e += this.sections[t3];
    return e;
  }
  get newLength() {
    let e = 0;
    for (let t3 = 0; t3 < this.sections.length; t3 += 2) {
      let n11 = this.sections[t3 + 1];
      e += n11 < 0 ? this.sections[t3] : n11;
    }
    return e;
  }
  get empty() {
    return this.sections.length == 0 || this.sections.length == 2 && this.sections[1] < 0;
  }
  iterGaps(e) {
    for (let t3 = 0, n11 = 0, i2 = 0; t3 < this.sections.length; ) {
      let r2 = this.sections[t3++], l9 = this.sections[t3++];
      l9 < 0 ? (e(n11, i2, r2), i2 += r2) : i2 += l9, n11 += r2;
    }
  }
  iterChangedRanges(e, t3 = false) {
    ue(this, e, t3);
  }
  get invertedDesc() {
    let e = [];
    for (let t3 = 0; t3 < this.sections.length; ) {
      let n11 = this.sections[t3++], i2 = this.sections[t3++];
      i2 < 0 ? e.push(n11, i2) : e.push(i2, n11);
    }
    return new s4(e);
  }
  composeDesc(e) {
    return this.empty ? e : e.empty ? this : Je(this, e);
  }
  mapDesc(e, t3 = false) {
    return e.empty ? this : ce(this, e, t3);
  }
  mapPos(e, t3 = -1, n11 = b.Simple) {
    let i2 = 0, r2 = 0;
    for (let l9 = 0; l9 < this.sections.length; ) {
      let h = this.sections[l9++], o3 = this.sections[l9++], a2 = i2 + h;
      if (o3 < 0) {
        if (a2 > e) return r2 + (e - i2);
        r2 += h;
      } else {
        if (n11 != b.Simple && a2 >= e && (n11 == b.TrackDel && i2 < e && a2 > e || n11 == b.TrackBefore && i2 < e || n11 == b.TrackAfter && a2 > e)) return null;
        if (a2 > e || a2 == e && t3 < 0 && !h) return e == i2 || t3 < 0 ? r2 : r2 + o3;
        r2 += o3;
      }
      i2 = a2;
    }
    if (e > i2) throw new RangeError(`Position ${e} is out of range for changeset of length ${i2}`);
    return r2;
  }
  touchesRange(e, t3 = e) {
    for (let n11 = 0, i2 = 0; n11 < this.sections.length && i2 <= t3; ) {
      let r2 = this.sections[n11++], l9 = this.sections[n11++], h = i2 + r2;
      if (l9 >= 0 && i2 <= t3 && h >= e) return i2 < e && h > t3 ? "cover" : true;
      i2 = h;
    }
    return false;
  }
  toString() {
    let e = "";
    for (let t3 = 0; t3 < this.sections.length; ) {
      let n11 = this.sections[t3++], i2 = this.sections[t3++];
      e += (e ? " " : "") + n11 + (i2 >= 0 ? ":" + i2 : "");
    }
    return e;
  }
  toJSON() {
    return this.sections;
  }
  static fromJSON(e) {
    if (!Array.isArray(e) || e.length % 2 || e.some((t3) => typeof t3 != "number")) throw new RangeError("Invalid JSON representation of ChangeDesc");
    return new s4(e);
  }
  static create(e) {
    return new s4(e);
  }
};
var P = class s5 extends C {
  constructor(e, t3) {
    super(e), this.inserted = t3;
  }
  apply(e) {
    if (this.length != e.length) throw new RangeError("Applying change set to a document with the wrong length");
    return ue(this, (t3, n11, i2, r2, l9) => e = e.replace(i2, i2 + (n11 - t3), l9), false), e;
  }
  mapDesc(e, t3 = false) {
    return ce(this, e, t3, true);
  }
  invert(e) {
    let t3 = this.sections.slice(), n11 = [];
    for (let i2 = 0, r2 = 0; i2 < t3.length; i2 += 2) {
      let l9 = t3[i2], h = t3[i2 + 1];
      if (h >= 0) {
        t3[i2] = h, t3[i2 + 1] = l9;
        let o3 = i2 >> 1;
        for (; n11.length < o3; ) n11.push(m.empty);
        n11.push(l9 ? e.slice(r2, r2 + l9) : m.empty);
      }
      r2 += l9;
    }
    return new s5(t3, n11);
  }
  compose(e) {
    return this.empty ? e : e.empty ? this : Je(this, e, true);
  }
  map(e, t3 = false) {
    return e.empty ? this : ce(this, e, t3, true);
  }
  iterChanges(e, t3 = false) {
    ue(this, e, t3);
  }
  get desc() {
    return C.create(this.sections);
  }
  filter(e) {
    let t3 = [], n11 = [], i2 = [], r2 = new M(this);
    e: for (let l9 = 0, h = 0; ; ) {
      let o3 = l9 == e.length ? 1e9 : e[l9++];
      for (; h < o3 || h == o3 && r2.len == 0; ) {
        if (r2.done) break e;
        let f = Math.min(r2.len, o3 - h);
        w(i2, f, -1);
        let u2 = r2.ins == -1 ? -1 : r2.off == 0 ? r2.ins : 0;
        w(t3, f, u2), u2 > 0 && R(n11, t3, r2.text), r2.forward(f), h += f;
      }
      let a2 = e[l9++];
      for (; h < a2; ) {
        if (r2.done) break e;
        let f = Math.min(r2.len, a2 - h);
        w(t3, f, -1), w(i2, f, r2.ins == -1 ? -1 : r2.off == 0 ? r2.ins : 0), r2.forward(f), h += f;
      }
    }
    return {
      changes: new s5(t3, n11),
      filtered: C.create(i2)
    };
  }
  toJSON() {
    let e = [];
    for (let t3 = 0; t3 < this.sections.length; t3 += 2) {
      let n11 = this.sections[t3], i2 = this.sections[t3 + 1];
      i2 < 0 ? e.push(n11) : i2 == 0 ? e.push([
        n11
      ]) : e.push([
        n11
      ].concat(this.inserted[t3 >> 1].toJSON()));
    }
    return e;
  }
  static of(e, t3, n11) {
    let i2 = [], r2 = [], l9 = 0, h = null;
    function o3(f = false) {
      if (!f && !i2.length) return;
      l9 < t3 && w(i2, t3 - l9, -1);
      let u2 = new s5(i2, r2);
      h = h ? h.compose(u2.map(h)) : u2, i2 = [], r2 = [], l9 = 0;
    }
    function a2(f) {
      if (Array.isArray(f)) for (let u2 of f) a2(u2);
      else if (f instanceof s5) {
        if (f.length != t3) throw new RangeError(`Mismatched change set length (got ${f.length}, expected ${t3})`);
        o3(), h = h ? h.compose(f.map(h)) : f;
      } else {
        let { from: u2, to: c3 = u2, insert: d } = f;
        if (u2 > c3 || u2 < 0 || c3 > t3) throw new RangeError(`Invalid change range ${u2} to ${c3} (in doc of length ${t3})`);
        let g3 = d ? typeof d == "string" ? m.of(d.split(n11 || fe)) : d : m.empty, A6 = g3.length;
        if (u2 == c3 && A6 == 0) return;
        u2 < l9 && o3(), u2 > l9 && w(i2, u2 - l9, -1), w(i2, c3 - u2, A6), R(r2, i2, g3), l9 = c3;
      }
    }
    return a2(e), o3(!h), h;
  }
  static empty(e) {
    return new s5(e ? [
      e,
      -1
    ] : [], []);
  }
  static fromJSON(e) {
    if (!Array.isArray(e)) throw new RangeError("Invalid JSON representation of ChangeSet");
    let t3 = [], n11 = [];
    for (let i2 = 0; i2 < e.length; i2++) {
      let r2 = e[i2];
      if (typeof r2 == "number") t3.push(r2, -1);
      else {
        if (!Array.isArray(r2) || typeof r2[0] != "number" || r2.some((l9, h) => h && typeof l9 != "string")) throw new RangeError("Invalid JSON representation of ChangeSet");
        if (r2.length == 1) t3.push(r2[0], 0);
        else {
          for (; n11.length < i2; ) n11.push(m.empty);
          n11[i2] = m.of(r2.slice(1)), t3.push(r2[0], n11[i2].length);
        }
      }
    }
    return new s5(t3, n11);
  }
  static createSet(e, t3) {
    return new s5(e, t3);
  }
};
function w(s45, e, t3, n11 = false) {
  if (e == 0 && t3 <= 0) return;
  let i2 = s45.length - 2;
  i2 >= 0 && t3 <= 0 && t3 == s45[i2 + 1] ? s45[i2] += e : e == 0 && s45[i2] == 0 ? s45[i2 + 1] += t3 : n11 ? (s45[i2] += e, s45[i2 + 1] += t3) : s45.push(e, t3);
}
function R(s45, e, t3) {
  if (t3.length == 0) return;
  let n11 = e.length - 2 >> 1;
  if (n11 < s45.length) s45[s45.length - 1] = s45[s45.length - 1].append(t3);
  else {
    for (; s45.length < n11; ) s45.push(m.empty);
    s45.push(t3);
  }
}
function ue(s45, e, t3) {
  let n11 = s45.inserted;
  for (let i2 = 0, r2 = 0, l9 = 0; l9 < s45.sections.length; ) {
    let h = s45.sections[l9++], o3 = s45.sections[l9++];
    if (o3 < 0) i2 += h, r2 += h;
    else {
      let a2 = i2, f = r2, u2 = m.empty;
      for (; a2 += h, f += o3, o3 && n11 && (u2 = u2.append(n11[l9 - 2 >> 1])), !(t3 || l9 == s45.sections.length || s45.sections[l9 + 1] < 0); ) h = s45.sections[l9++], o3 = s45.sections[l9++];
      e(i2, a2, r2, f, u2), i2 = a2, r2 = f;
    }
  }
}
function ce(s45, e, t3, n11 = false) {
  let i2 = [], r2 = n11 ? [] : null, l9 = new M(s45), h = new M(e);
  for (let o3 = 0, a2 = 0; ; ) if (l9.ins == -1) o3 += l9.len, l9.next();
  else if (h.ins == -1 && a2 < o3) {
    let f = Math.min(h.len, o3 - a2);
    h.forward(f), w(i2, f, -1), a2 += f;
  } else if (h.ins >= 0 && (l9.done || a2 < o3 || a2 == o3 && (h.len < l9.len || h.len == l9.len && !t3))) {
    for (w(i2, h.ins, -1); o3 > a2 && !l9.done && o3 + l9.len < a2 + h.len; ) o3 += l9.len, l9.next();
    a2 += h.len, h.next();
  } else if (l9.ins >= 0) {
    let f = 0, u2 = o3 + l9.len;
    for (; ; ) if (h.ins >= 0 && a2 > o3 && a2 + h.len < u2) f += h.ins, a2 += h.len, h.next();
    else if (h.ins == -1 && a2 < u2) {
      let c3 = Math.min(h.len, u2 - a2);
      f += c3, h.forward(c3), a2 += c3;
    } else break;
    w(i2, f, l9.ins), r2 && R(r2, i2, l9.text), o3 = u2, l9.next();
  } else {
    if (l9.done && h.done) return r2 ? P.createSet(i2, r2) : C.create(i2);
    throw new Error("Mismatched change set lengths");
  }
}
function Je(s45, e, t3 = false) {
  let n11 = [], i2 = t3 ? [] : null, r2 = new M(s45), l9 = new M(e);
  for (let h = false; ; ) {
    if (r2.done && l9.done) return i2 ? P.createSet(n11, i2) : C.create(n11);
    if (r2.ins == 0) w(n11, r2.len, 0, h), r2.next();
    else if (l9.len == 0 && !l9.done) w(n11, 0, l9.ins, h), i2 && R(i2, n11, l9.text), l9.next();
    else {
      if (r2.done || l9.done) throw new Error("Mismatched change set lengths");
      {
        let o3 = Math.min(r2.len2, l9.len), a2 = n11.length;
        if (r2.ins == -1) {
          let f = l9.ins == -1 ? -1 : l9.off ? 0 : l9.ins;
          w(n11, o3, f, h), i2 && f && R(i2, n11, l9.text);
        } else l9.ins == -1 ? (w(n11, r2.off ? 0 : r2.len, o3, h), i2 && R(i2, n11, r2.textBit(o3))) : (w(n11, r2.off ? 0 : r2.len, l9.off ? 0 : l9.ins, h), i2 && !l9.off && R(i2, n11, l9.text));
        h = (r2.ins > o3 || l9.ins >= 0 && l9.len > o3) && (h || n11.length > a2), r2.forward2(o3), l9.forward(o3);
      }
    }
  }
}
var M = class {
  constructor(e) {
    this.set = e, this.i = 0, this.next();
  }
  next() {
    let { sections: e } = this.set;
    this.i < e.length ? (this.len = e[this.i++], this.ins = e[this.i++]) : (this.len = 0, this.ins = -2), this.off = 0;
  }
  get done() {
    return this.ins == -2;
  }
  get len2() {
    return this.ins < 0 ? this.len : this.ins;
  }
  get text() {
    let { inserted: e } = this.set, t3 = this.i - 2 >> 1;
    return t3 >= e.length ? m.empty : e[t3];
  }
  textBit(e) {
    let { inserted: t3 } = this.set, n11 = this.i - 2 >> 1;
    return n11 >= t3.length && !e ? m.empty : t3[n11].slice(this.off, e == null ? void 0 : this.off + e);
  }
  forward(e) {
    e == this.len ? this.next() : (this.len -= e, this.off += e);
  }
  forward2(e) {
    this.ins == -1 ? this.forward(e) : e == this.ins ? this.next() : (this.ins -= e, this.off += e);
  }
};
var L = class s6 {
  constructor(e, t3, n11) {
    this.from = e, this.to = t3, this.flags = n11;
  }
  get anchor() {
    return this.flags & 16 ? this.to : this.from;
  }
  get head() {
    return this.flags & 16 ? this.from : this.to;
  }
  get empty() {
    return this.from == this.to;
  }
  get assoc() {
    return this.flags & 4 ? -1 : this.flags & 8 ? 1 : 0;
  }
  get bidiLevel() {
    let e = this.flags & 3;
    return e == 3 ? null : e;
  }
  get goalColumn() {
    let e = this.flags >> 5;
    return e == 33554431 ? void 0 : e;
  }
  map(e, t3 = -1) {
    let n11, i2;
    return this.empty ? n11 = i2 = e.mapPos(this.from, t3) : (n11 = e.mapPos(this.from, 1), i2 = e.mapPos(this.to, -1)), n11 == this.from && i2 == this.to ? this : new s6(n11, i2, this.flags);
  }
  extend(e, t3 = e) {
    if (e <= this.anchor && t3 >= this.anchor) return x.range(e, t3);
    let n11 = Math.abs(e - this.anchor) > Math.abs(t3 - this.anchor) ? e : t3;
    return x.range(this.anchor, n11);
  }
  eq(e) {
    return this.anchor == e.anchor && this.head == e.head;
  }
  toJSON() {
    return {
      anchor: this.anchor,
      head: this.head
    };
  }
  static fromJSON(e) {
    if (!e || typeof e.anchor != "number" || typeof e.head != "number") throw new RangeError("Invalid JSON representation for SelectionRange");
    return x.range(e.anchor, e.head);
  }
  static create(e, t3, n11) {
    return new s6(e, t3, n11);
  }
};
var x = class s7 {
  constructor(e, t3) {
    this.ranges = e, this.mainIndex = t3;
  }
  map(e, t3 = -1) {
    return e.empty ? this : s7.create(this.ranges.map((n11) => n11.map(e, t3)), this.mainIndex);
  }
  eq(e) {
    if (this.ranges.length != e.ranges.length || this.mainIndex != e.mainIndex) return false;
    for (let t3 = 0; t3 < this.ranges.length; t3++) if (!this.ranges[t3].eq(e.ranges[t3])) return false;
    return true;
  }
  get main() {
    return this.ranges[this.mainIndex];
  }
  asSingle() {
    return this.ranges.length == 1 ? this : new s7([
      this.main
    ], 0);
  }
  addRange(e, t3 = true) {
    return s7.create([
      e
    ].concat(this.ranges), t3 ? 0 : this.mainIndex + 1);
  }
  replaceRange(e, t3 = this.mainIndex) {
    let n11 = this.ranges.slice();
    return n11[t3] = e, s7.create(n11, this.mainIndex);
  }
  toJSON() {
    return {
      ranges: this.ranges.map((e) => e.toJSON()),
      main: this.mainIndex
    };
  }
  static fromJSON(e) {
    if (!e || !Array.isArray(e.ranges) || typeof e.main != "number" || e.main >= e.ranges.length) throw new RangeError("Invalid JSON representation for EditorSelection");
    return new s7(e.ranges.map((t3) => L.fromJSON(t3)), e.main);
  }
  static single(e, t3 = e) {
    return new s7([
      s7.range(e, t3)
    ], 0);
  }
  static create(e, t3 = 0) {
    if (e.length == 0) throw new RangeError("A selection needs at least one range");
    for (let n11 = 0, i2 = 0; i2 < e.length; i2++) {
      let r2 = e[i2];
      if (r2.empty ? r2.from <= n11 : r2.from < n11) return s7.normalized(e.slice(), t3);
      n11 = r2.to;
    }
    return new s7(e, t3);
  }
  static cursor(e, t3 = 0, n11, i2) {
    return L.create(e, e, (t3 == 0 ? 0 : t3 < 0 ? 4 : 8) | (n11 == null ? 3 : Math.min(2, n11)) | (i2 ?? 33554431) << 5);
  }
  static range(e, t3, n11) {
    let i2 = (n11 ?? 33554431) << 5;
    return t3 < e ? L.create(t3, e, 16 | i2 | 8) : L.create(e, t3, i2 | (t3 > e ? 4 : 0));
  }
  static normalized(e, t3 = 0) {
    let n11 = e[t3];
    e.sort((i2, r2) => i2.from - r2.from), t3 = e.indexOf(n11);
    for (let i2 = 1; i2 < e.length; i2++) {
      let r2 = e[i2], l9 = e[i2 - 1];
      if (r2.empty ? r2.from <= l9.to : r2.from < l9.to) {
        let h = l9.from, o3 = Math.max(r2.to, l9.to);
        i2 <= t3 && t3--, e.splice(--i2, 2, r2.anchor > r2.head ? s7.range(o3, h) : s7.range(h, o3));
      }
    }
    return new s7(e, t3);
  }
};
function Le(s45, e) {
  for (let t3 of s45.ranges) if (t3.to > e) throw new RangeError("Selection points outside of document");
}
var ye = 0;
var y = class s8 {
  constructor(e, t3, n11, i2, r2) {
    this.combine = e, this.compareInput = t3, this.compare = n11, this.isStatic = i2, this.extensions = r2, this.id = ye++, this.default = e([]);
  }
  static define(e = {}) {
    return new s8(e.combine || ((t3) => t3), e.compareInput || ((t3, n11) => t3 === n11), e.compare || (e.combine ? (t3, n11) => t3 === n11 : Se), !!e.static, e.enables);
  }
  of(e) {
    return new V([], this, 0, e);
  }
  compute(e, t3) {
    if (this.isStatic) throw new Error("Can't compute a static facet");
    return new V(e, this, 1, t3);
  }
  computeN(e, t3) {
    if (this.isStatic) throw new Error("Can't compute a static facet");
    return new V(e, this, 2, t3);
  }
  from(e, t3) {
    return t3 || (t3 = (n11) => n11), this.compute([
      e
    ], (n11) => t3(n11.field(e)));
  }
};
function Se(s45, e) {
  return s45 == e || s45.length == e.length && s45.every((t3, n11) => t3 === e[n11]);
}
var V = class {
  constructor(e, t3, n11, i2) {
    this.dependencies = e, this.facet = t3, this.type = n11, this.value = i2, this.id = ye++;
  }
  dynamicSlot(e) {
    var t3;
    let n11 = this.value, i2 = this.facet.compareInput, r2 = this.id, l9 = e[r2] >> 1, h = this.type == 2, o3 = false, a2 = false, f = [];
    for (let u2 of this.dependencies) u2 == "doc" ? o3 = true : u2 == "selection" ? a2 = true : (((t3 = e[u2.id]) !== null && t3 !== void 0 ? t3 : 1) & 1) == 0 && f.push(e[u2.id]);
    return {
      create(u2) {
        return u2.values[l9] = n11(u2), 1;
      },
      update(u2, c3) {
        if (o3 && c3.docChanged || a2 && (c3.docChanged || c3.selection) || de(u2, f)) {
          let d = n11(u2);
          if (h ? !Ee(d, u2.values[l9], i2) : !i2(d, u2.values[l9])) return u2.values[l9] = d, 1;
        }
        return 0;
      },
      reconfigure: (u2, c3) => {
        let d = n11(u2), g3 = c3.config.address[r2];
        if (g3 != null) {
          let A6 = ie(c3, g3);
          if (this.dependencies.every((p2) => p2 instanceof y ? c3.facet(p2) === u2.facet(p2) : p2 instanceof $ ? c3.field(p2, false) == u2.field(p2, false) : true) || (h ? Ee(d, A6, i2) : i2(d, A6))) return u2.values[l9] = A6, 0;
        }
        return u2.values[l9] = d, 1;
      }
    };
  }
};
function Ee(s45, e, t3) {
  if (s45.length != e.length) return false;
  for (let n11 = 0; n11 < s45.length; n11++) if (!t3(s45[n11], e[n11])) return false;
  return true;
}
function de(s45, e) {
  let t3 = false;
  for (let n11 of e) U(s45, n11) & 1 && (t3 = true);
  return t3;
}
function Ke(s45, e, t3) {
  let n11 = t3.map((o3) => s45[o3.id]), i2 = t3.map((o3) => o3.type), r2 = n11.filter((o3) => !(o3 & 1)), l9 = s45[e.id] >> 1;
  function h(o3) {
    let a2 = [];
    for (let f = 0; f < n11.length; f++) {
      let u2 = ie(o3, n11[f]);
      if (i2[f] == 2) for (let c3 of u2) a2.push(c3);
      else a2.push(u2);
    }
    return e.combine(a2);
  }
  return {
    create(o3) {
      for (let a2 of n11) U(o3, a2);
      return o3.values[l9] = h(o3), 1;
    },
    update(o3, a2) {
      if (!de(o3, r2)) return 0;
      let f = h(o3);
      return e.compare(f, o3.values[l9]) ? 0 : (o3.values[l9] = f, 1);
    },
    reconfigure(o3, a2) {
      let f = de(o3, n11), u2 = a2.config.facets[e.id], c3 = a2.facet(e);
      if (u2 && !f && Se(t3, u2)) return o3.values[l9] = c3, 0;
      let d = h(o3);
      return e.compare(d, c3) ? (o3.values[l9] = c3, 0) : (o3.values[l9] = d, 1);
    }
  };
}
var Oe = y.define({
  static: true
});
var $ = class s9 {
  constructor(e, t3, n11, i2, r2) {
    this.id = e, this.createF = t3, this.updateF = n11, this.compareF = i2, this.spec = r2, this.provides = void 0;
  }
  static define(e) {
    let t3 = new s9(ye++, e.create, e.update, e.compare || ((n11, i2) => n11 === i2), e);
    return e.provide && (t3.provides = e.provide(t3)), t3;
  }
  create(e) {
    let t3 = e.facet(Oe).find((n11) => n11.field == this);
    return (t3?.create || this.createF)(e);
  }
  slot(e) {
    let t3 = e[this.id] >> 1;
    return {
      create: (n11) => (n11.values[t3] = this.create(n11), 1),
      update: (n11, i2) => {
        let r2 = n11.values[t3], l9 = this.updateF(r2, i2);
        return this.compareF(r2, l9) ? 0 : (n11.values[t3] = l9, 1);
      },
      reconfigure: (n11, i2) => i2.config.address[this.id] != null ? (n11.values[t3] = i2.field(this), 0) : (n11.values[t3] = this.create(n11), 1)
    };
  }
  init(e) {
    return [
      this,
      Oe.of({
        field: this,
        create: e
      })
    ];
  }
  get extension() {
    return this;
  }
};
var J = {
  lowest: 4,
  low: 3,
  default: 2,
  high: 1,
  highest: 0
};
function W(s45) {
  return (e) => new ee(e, s45);
}
var lt = {
  highest: W(J.highest),
  high: W(J.high),
  default: W(J.default),
  low: W(J.low),
  lowest: W(J.lowest)
};
var ee = class {
  constructor(e, t3) {
    this.inner = e, this.prec = t3;
  }
};
var te = class s10 {
  of(e) {
    return new G(this, e);
  }
  reconfigure(e) {
    return s10.reconfigure.of({
      compartment: this,
      extension: e
    });
  }
  get(e) {
    return e.config.compartments.get(this);
  }
};
var G = class {
  constructor(e, t3) {
    this.compartment = e, this.inner = t3;
  }
};
var ne = class s11 {
  constructor(e, t3, n11, i2, r2, l9) {
    for (this.base = e, this.compartments = t3, this.dynamicSlots = n11, this.address = i2, this.staticValues = r2, this.facets = l9, this.statusTemplate = []; this.statusTemplate.length < n11.length; ) this.statusTemplate.push(0);
  }
  staticFacet(e) {
    let t3 = this.address[e.id];
    return t3 == null ? e.default : this.staticValues[t3 >> 1];
  }
  static resolve(e, t3, n11) {
    let i2 = [], r2 = /* @__PURE__ */ Object.create(null), l9 = /* @__PURE__ */ new Map();
    for (let c3 of Qe(e, t3, l9)) c3 instanceof $ ? i2.push(c3) : (r2[c3.facet.id] || (r2[c3.facet.id] = [])).push(c3);
    let h = /* @__PURE__ */ Object.create(null), o3 = [], a2 = [];
    for (let c3 of i2) h[c3.id] = a2.length << 1, a2.push((d) => c3.slot(d));
    let f = n11?.config.facets;
    for (let c3 in r2) {
      let d = r2[c3], g3 = d[0].facet, A6 = f && f[c3] || [];
      if (d.every((p2) => p2.type == 0)) if (h[g3.id] = o3.length << 1 | 1, Se(A6, d)) o3.push(n11.facet(g3));
      else {
        let p2 = g3.combine(d.map((le3) => le3.value));
        o3.push(n11 && g3.compare(p2, n11.facet(g3)) ? n11.facet(g3) : p2);
      }
      else {
        for (let p2 of d) p2.type == 0 ? (h[p2.id] = o3.length << 1 | 1, o3.push(p2.value)) : (h[p2.id] = a2.length << 1, a2.push((le3) => p2.dynamicSlot(le3)));
        h[g3.id] = a2.length << 1, a2.push((p2) => Ke(p2, g3, d));
      }
    }
    let u2 = a2.map((c3) => c3(h));
    return new s11(e, l9, u2, h, o3, r2);
  }
};
function Qe(s45, e, t3) {
  let n11 = [
    [],
    [],
    [],
    [],
    []
  ], i2 = /* @__PURE__ */ new Map();
  function r2(l9, h) {
    let o3 = i2.get(l9);
    if (o3 != null) {
      if (o3 <= h) return;
      let a2 = n11[o3].indexOf(l9);
      a2 > -1 && n11[o3].splice(a2, 1), l9 instanceof G && t3.delete(l9.compartment);
    }
    if (i2.set(l9, h), Array.isArray(l9)) for (let a2 of l9) r2(a2, h);
    else if (l9 instanceof G) {
      if (t3.has(l9.compartment)) throw new RangeError("Duplicate use of compartment in extensions");
      let a2 = e.get(l9.compartment) || l9.inner;
      t3.set(l9.compartment, a2), r2(a2, h);
    } else if (l9 instanceof ee) r2(l9.inner, l9.prec);
    else if (l9 instanceof $) n11[h].push(l9), l9.provides && r2(l9.provides, h);
    else if (l9 instanceof V) n11[h].push(l9), l9.facet.extensions && r2(l9.facet.extensions, h);
    else {
      let a2 = l9.extension;
      if (!a2) throw new Error(`Unrecognized extension value in extension set (${l9}). This sometimes happens because multiple instances of @codemirror/state are loaded, breaking instanceof checks.`);
      r2(a2, h);
    }
  }
  return r2(s45, J.default), n11.reduce((l9, h) => l9.concat(h));
}
function U(s45, e) {
  if (e & 1) return 2;
  let t3 = e >> 1, n11 = s45.status[t3];
  if (n11 == 4) throw new Error("Cyclic dependency between fields and/or facets");
  if (n11 & 2) return n11;
  s45.status[t3] = 4;
  let i2 = s45.computeSlot(s45, s45.config.dynamicSlots[t3]);
  return s45.status[t3] = 2 | i2;
}
function ie(s45, e) {
  return e & 1 ? s45.config.staticValues[e >> 1] : s45.values[e >> 1];
}
var Ne = y.define();
var De = y.define({
  combine: (s45) => s45.some((e) => e),
  static: true
});
var Ve = y.define({
  combine: (s45) => s45.length ? s45[0] : void 0,
  static: true
});
var qe = y.define();
var $e = y.define();
var ze = y.define();
var We = y.define({
  combine: (s45) => s45.length ? s45[0] : false
});
var F = class {
  constructor(e, t3) {
    this.type = e, this.value = t3;
  }
  static define() {
    return new ge();
  }
};
var ge = class {
  of(e) {
    return new F(this, e);
  }
};
var pe = class {
  constructor(e) {
    this.map = e;
  }
  of(e) {
    return new v(this, e);
  }
};
var v = class s12 {
  constructor(e, t3) {
    this.type = e, this.value = t3;
  }
  map(e) {
    let t3 = this.type.map(this.value, e);
    return t3 === void 0 ? void 0 : t3 == this.value ? this : new s12(this.type, t3);
  }
  is(e) {
    return this.type == e;
  }
  static define(e = {}) {
    return new pe(e.map || ((t3) => t3));
  }
  static mapEffects(e, t3) {
    if (!e.length) return e;
    let n11 = [];
    for (let i2 of e) {
      let r2 = i2.map(t3);
      r2 && n11.push(r2);
    }
    return n11;
  }
};
v.reconfigure = v.define();
v.appendConfig = v.define();
var S = class s13 {
  constructor(e, t3, n11, i2, r2, l9) {
    this.startState = e, this.changes = t3, this.selection = n11, this.effects = i2, this.annotations = r2, this.scrollIntoView = l9, this._doc = null, this._state = null, n11 && Le(n11, t3.newLength), r2.some((h) => h.type == s13.time) || (this.annotations = r2.concat(s13.time.of(Date.now())));
  }
  static create(e, t3, n11, i2, r2, l9) {
    return new s13(e, t3, n11, i2, r2, l9);
  }
  get newDoc() {
    return this._doc || (this._doc = this.changes.apply(this.startState.doc));
  }
  get newSelection() {
    return this.selection || this.startState.selection.map(this.changes);
  }
  get state() {
    return this._state || this.startState.applyTransaction(this), this._state;
  }
  annotation(e) {
    for (let t3 of this.annotations) if (t3.type == e) return t3.value;
  }
  get docChanged() {
    return !this.changes.empty;
  }
  get reconfigured() {
    return this.startState.config != this.state.config;
  }
  isUserEvent(e) {
    let t3 = this.annotation(s13.userEvent);
    return !!(t3 && (t3 == e || t3.length > e.length && t3.slice(0, e.length) == e && t3[e.length] == "."));
  }
};
S.time = F.define();
S.userEvent = F.define();
S.addToHistory = F.define();
S.remote = F.define();
function Xe(s45, e) {
  let t3 = [];
  for (let n11 = 0, i2 = 0; ; ) {
    let r2, l9;
    if (n11 < s45.length && (i2 == e.length || e[i2] >= s45[n11])) r2 = s45[n11++], l9 = s45[n11++];
    else if (i2 < e.length) r2 = e[i2++], l9 = e[i2++];
    else return t3;
    !t3.length || t3[t3.length - 1] < r2 ? t3.push(r2, l9) : t3[t3.length - 1] < l9 && (t3[t3.length - 1] = l9);
  }
}
function Ue(s45, e, t3) {
  var n11;
  let i2, r2, l9;
  return t3 ? (i2 = e.changes, r2 = P.empty(e.changes.length), l9 = s45.changes.compose(e.changes)) : (i2 = e.changes.map(s45.changes), r2 = s45.changes.mapDesc(e.changes, true), l9 = s45.changes.compose(i2)), {
    changes: l9,
    selection: e.selection ? e.selection.map(r2) : (n11 = s45.selection) === null || n11 === void 0 ? void 0 : n11.map(i2),
    effects: v.mapEffects(s45.effects, i2).concat(v.mapEffects(e.effects, r2)),
    annotations: s45.annotations.length ? s45.annotations.concat(e.annotations) : e.annotations,
    scrollIntoView: s45.scrollIntoView || e.scrollIntoView
  };
}
function me(s45, e, t3) {
  let n11 = e.selection, i2 = q(e.annotations);
  return e.userEvent && (i2 = i2.concat(S.userEvent.of(e.userEvent))), {
    changes: e.changes instanceof P ? e.changes : P.of(e.changes || [], t3, s45.facet(Ve)),
    selection: n11 && (n11 instanceof x ? n11 : x.single(n11.anchor, n11.head)),
    effects: q(e.effects),
    annotations: i2,
    scrollIntoView: !!e.scrollIntoView
  };
}
function Ge(s45, e, t3) {
  let n11 = me(s45, e.length ? e[0] : {}, s45.doc.length);
  e.length && e[0].filter === false && (t3 = false);
  for (let r2 = 1; r2 < e.length; r2++) {
    e[r2].filter === false && (t3 = false);
    let l9 = !!e[r2].sequential;
    n11 = Ue(n11, me(s45, e[r2], l9 ? n11.changes.newLength : s45.doc.length), l9);
  }
  let i2 = S.create(s45, n11.changes, n11.selection, n11.effects, n11.annotations, n11.scrollIntoView);
  return _e(t3 ? Ye(i2) : i2);
}
function Ye(s45) {
  let e = s45.startState, t3 = true;
  for (let i2 of e.facet(qe)) {
    let r2 = i2(s45);
    if (r2 === false) {
      t3 = false;
      break;
    }
    Array.isArray(r2) && (t3 = t3 === true ? r2 : Xe(t3, r2));
  }
  if (t3 !== true) {
    let i2, r2;
    if (t3 === false) r2 = s45.changes.invertedDesc, i2 = P.empty(e.doc.length);
    else {
      let l9 = s45.changes.filter(t3);
      i2 = l9.changes, r2 = l9.filtered.invertedDesc;
    }
    s45 = S.create(e, i2, s45.selection && s45.selection.map(r2), v.mapEffects(s45.effects, r2), s45.annotations, s45.scrollIntoView);
  }
  let n11 = e.facet($e);
  for (let i2 = n11.length - 1; i2 >= 0; i2--) {
    let r2 = n11[i2](s45);
    r2 instanceof S ? s45 = r2 : Array.isArray(r2) && r2.length == 1 && r2[0] instanceof S ? s45 = r2[0] : s45 = Ge(e, q(r2), false);
  }
  return s45;
}
function _e(s45) {
  let e = s45.startState, t3 = e.facet(ze), n11 = s45;
  for (let i2 = t3.length - 1; i2 >= 0; i2--) {
    let r2 = t3[i2](s45);
    r2 && Object.keys(r2).length && (n11 = Ue(s45, me(e, r2, s45.changes.newLength), true));
  }
  return n11 == s45 ? s45 : S.create(e, s45.changes, s45.selection, n11.effects, n11.annotations, n11.scrollIntoView);
}
var et = [];
function q(s45) {
  return s45 == null ? et : Array.isArray(s45) ? s45 : [
    s45
  ];
}
var E = function(s45) {
  return s45[s45.Word = 0] = "Word", s45[s45.Space = 1] = "Space", s45[s45.Other = 2] = "Other", s45;
}(E || (E = {}));
var tt = /[\u00df\u0587\u0590-\u05f4\u0600-\u06ff\u3040-\u309f\u30a0-\u30ff\u3400-\u4db5\u4e00-\u9fcc\uac00-\ud7af]/;
var we;
try {
  we = new RegExp("[\\p{Alphabetic}\\p{Number}_]", "u");
} catch {
}
function nt(s45) {
  if (we) return we.test(s45);
  for (let e = 0; e < s45.length; e++) {
    let t3 = s45[e];
    if (/\w/.test(t3) || t3 > "\x80" && (t3.toUpperCase() != t3.toLowerCase() || tt.test(t3))) return true;
  }
  return false;
}
function it(s45) {
  return (e) => {
    if (!/\S/.test(e)) return E.Space;
    if (nt(e)) return E.Word;
    for (let t3 = 0; t3 < s45.length; t3++) if (e.indexOf(s45[t3]) > -1) return E.Word;
    return E.Other;
  };
}
var I = class s14 {
  constructor(e, t3, n11, i2, r2, l9) {
    this.config = e, this.doc = t3, this.selection = n11, this.values = i2, this.status = e.statusTemplate.slice(), this.computeSlot = r2, l9 && (l9._state = this);
    for (let h = 0; h < this.config.dynamicSlots.length; h++) U(this, h << 1);
    this.computeSlot = null;
  }
  field(e, t3 = true) {
    let n11 = this.config.address[e.id];
    if (n11 == null) {
      if (t3) throw new RangeError("Field is not present in this state");
      return;
    }
    return U(this, n11), ie(this, n11);
  }
  update(...e) {
    return Ge(this, e, true);
  }
  applyTransaction(e) {
    let t3 = this.config, { base: n11, compartments: i2 } = t3;
    for (let l9 of e.effects) l9.is(te.reconfigure) ? (t3 && (i2 = /* @__PURE__ */ new Map(), t3.compartments.forEach((h, o3) => i2.set(o3, h)), t3 = null), i2.set(l9.value.compartment, l9.value.extension)) : l9.is(v.reconfigure) ? (t3 = null, n11 = l9.value) : l9.is(v.appendConfig) && (t3 = null, n11 = q(n11).concat(l9.value));
    let r2;
    t3 ? r2 = e.startState.values.slice() : (t3 = ne.resolve(n11, i2, this), r2 = new s14(t3, this.doc, this.selection, t3.dynamicSlots.map(() => null), (h, o3) => o3.reconfigure(h, this), null).values), new s14(t3, e.newDoc, e.newSelection, r2, (l9, h) => h.update(l9, e), e);
  }
  replaceSelection(e) {
    return typeof e == "string" && (e = this.toText(e)), this.changeByRange((t3) => ({
      changes: {
        from: t3.from,
        to: t3.to,
        insert: e
      },
      range: x.cursor(t3.from + e.length)
    }));
  }
  changeByRange(e) {
    let t3 = this.selection, n11 = e(t3.ranges[0]), i2 = this.changes(n11.changes), r2 = [
      n11.range
    ], l9 = q(n11.effects);
    for (let h = 1; h < t3.ranges.length; h++) {
      let o3 = e(t3.ranges[h]), a2 = this.changes(o3.changes), f = a2.map(i2);
      for (let c3 = 0; c3 < h; c3++) r2[c3] = r2[c3].map(f);
      let u2 = i2.mapDesc(a2, true);
      r2.push(o3.range.map(u2)), i2 = i2.compose(f), l9 = v.mapEffects(l9, f).concat(v.mapEffects(q(o3.effects), u2));
    }
    return {
      changes: i2,
      selection: x.create(r2, t3.mainIndex),
      effects: l9
    };
  }
  changes(e = []) {
    return e instanceof P ? e : P.of(e, this.doc.length, this.facet(s14.lineSeparator));
  }
  toText(e) {
    return m.of(e.split(this.facet(s14.lineSeparator) || fe));
  }
  sliceDoc(e = 0, t3 = this.doc.length) {
    return this.doc.sliceString(e, t3, this.lineBreak);
  }
  facet(e) {
    let t3 = this.config.address[e.id];
    return t3 == null ? e.default : (U(this, t3), ie(this, t3));
  }
  toJSON(e) {
    let t3 = {
      doc: this.sliceDoc(),
      selection: this.selection.toJSON()
    };
    if (e) for (let n11 in e) {
      let i2 = e[n11];
      i2 instanceof $ && (t3[n11] = i2.spec.toJSON(this.field(e[n11]), this));
    }
    return t3;
  }
  static fromJSON(e, t3 = {}, n11) {
    if (!e || typeof e.doc != "string") throw new RangeError("Invalid JSON representation for EditorState");
    let i2 = [];
    if (n11) for (let r2 in n11) {
      let l9 = n11[r2], h = e[r2];
      i2.push(l9.init((o3) => l9.spec.fromJSON(h, o3)));
    }
    return s14.create({
      doc: e.doc,
      selection: x.fromJSON(e.selection),
      extensions: t3.extensions ? i2.concat([
        t3.extensions
      ]) : i2
    });
  }
  static create(e = {}) {
    let t3 = ne.resolve(e.extensions || [], /* @__PURE__ */ new Map()), n11 = e.doc instanceof m ? e.doc : m.of((e.doc || "").split(t3.staticFacet(s14.lineSeparator) || fe)), i2 = e.selection ? e.selection instanceof x ? e.selection : x.single(e.selection.anchor, e.selection.head) : x.single(0);
    return Le(i2, n11.length), t3.staticFacet(De) || (i2 = i2.asSingle()), new s14(t3, n11, i2, t3.dynamicSlots.map(() => null), (r2, l9) => l9.create(r2), null);
  }
  get tabSize() {
    return this.facet(s14.tabSize);
  }
  get lineBreak() {
    return this.facet(s14.lineSeparator) || `
`;
  }
  get readOnly() {
    return this.facet(We);
  }
  phrase(e, ...t3) {
    for (let n11 of this.facet(s14.phrases)) if (Object.prototype.hasOwnProperty.call(n11, e)) {
      e = n11[e];
      break;
    }
    return t3.length && (e = e.replace(/\$(\$|\d*)/g, (n11, i2) => {
      if (i2 == "$") return "$";
      let r2 = +(i2 || 1);
      return r2 > t3.length ? n11 : t3[r2 - 1];
    })), e;
  }
  languageDataAt(e, t3, n11 = -1) {
    let i2 = [];
    for (let r2 of this.facet(Ne)) for (let l9 of r2(this, t3, n11)) Object.prototype.hasOwnProperty.call(l9, e) && i2.push(l9[e]);
    return i2;
  }
  charCategorizer(e) {
    return it(this.languageDataAt("wordChars", e).join(""));
  }
  wordAt(e) {
    let { text: t3, from: n11, length: i2 } = this.doc.lineAt(e), r2 = this.charCategorizer(e), l9 = e - n11, h = e - n11;
    for (; l9 > 0; ) {
      let o3 = _(t3, l9, false);
      if (r2(t3.slice(o3, l9)) != E.Word) break;
      l9 = o3;
    }
    for (; h < i2; ) {
      let o3 = _(t3, h);
      if (r2(t3.slice(h, o3)) != E.Word) break;
      h = o3;
    }
    return l9 == h ? null : x.range(l9 + n11, h + n11);
  }
};
I.allowMultipleSelections = De;
I.tabSize = y.define({
  combine: (s45) => s45.length ? s45[0] : 4
});
I.lineSeparator = Ve;
I.readOnly = We;
I.phrases = y.define({
  compare(s45, e) {
    let t3 = Object.keys(s45), n11 = Object.keys(e);
    return t3.length == n11.length && t3.every((i2) => s45[i2] == e[i2]);
  }
});
I.languageData = Ne;
I.changeFilter = qe;
I.transactionFilter = $e;
I.transactionExtender = ze;
te.reconfigure = v.define();
function ht(s45, e, t3 = {}) {
  let n11 = {};
  for (let i2 of s45) for (let r2 of Object.keys(i2)) {
    let l9 = i2[r2], h = n11[r2];
    if (h === void 0) n11[r2] = l9;
    else if (!(h === l9 || l9 === void 0)) if (Object.hasOwnProperty.call(t3, r2)) n11[r2] = t3[r2](h, l9);
    else throw new Error("Config merge conflict for field " + r2);
  }
  for (let i2 in e) n11[i2] === void 0 && (n11[i2] = e[i2]);
  return n11;
}
var z = class {
  eq(e) {
    return this == e;
  }
  range(e, t3 = e) {
    return j.create(e, t3, this);
  }
};
z.prototype.startSide = z.prototype.endSide = 0;
z.prototype.point = false;
z.prototype.mapMode = b.TrackDel;
var j = class s15 {
  constructor(e, t3, n11) {
    this.from = e, this.to = t3, this.value = n11;
  }
  static create(e, t3, n11) {
    return new s15(e, t3, n11);
  }
};
function ve(s45, e) {
  return s45.from - e.from || s45.value.startSide - e.value.startSide;
}
var xe = class s16 {
  constructor(e, t3, n11, i2) {
    this.from = e, this.to = t3, this.value = n11, this.maxPoint = i2;
  }
  get length() {
    return this.to[this.to.length - 1];
  }
  findIndex(e, t3, n11, i2 = 0) {
    let r2 = n11 ? this.to : this.from;
    for (let l9 = i2, h = r2.length; ; ) {
      if (l9 == h) return l9;
      let o3 = l9 + h >> 1, a2 = r2[o3] - e || (n11 ? this.value[o3].endSide : this.value[o3].startSide) - t3;
      if (o3 == l9) return a2 >= 0 ? l9 : h;
      a2 >= 0 ? h = o3 : l9 = o3 + 1;
    }
  }
  between(e, t3, n11, i2) {
    for (let r2 = this.findIndex(t3, -1e9, true), l9 = this.findIndex(n11, 1e9, false, r2); r2 < l9; r2++) if (i2(this.from[r2] + e, this.to[r2] + e, this.value[r2]) === false) return false;
  }
  map(e, t3) {
    let n11 = [], i2 = [], r2 = [], l9 = -1, h = -1;
    for (let o3 = 0; o3 < this.value.length; o3++) {
      let a2 = this.value[o3], f = this.from[o3] + e, u2 = this.to[o3] + e, c3, d;
      if (f == u2) {
        let g3 = t3.mapPos(f, a2.startSide, a2.mapMode);
        if (g3 == null || (c3 = d = g3, a2.startSide != a2.endSide && (d = t3.mapPos(f, a2.endSide), d < c3))) continue;
      } else if (c3 = t3.mapPos(f, a2.startSide), d = t3.mapPos(u2, a2.endSide), c3 > d || c3 == d && a2.startSide > 0 && a2.endSide <= 0) continue;
      (d - c3 || a2.endSide - a2.startSide) < 0 || (l9 < 0 && (l9 = c3), a2.point && (h = Math.max(h, d - c3)), n11.push(a2), i2.push(c3 - l9), r2.push(d - l9));
    }
    return {
      mapped: n11.length ? new s16(i2, r2, n11, h) : null,
      pos: l9
    };
  }
};
var O = class s17 {
  constructor(e, t3, n11, i2) {
    this.chunkPos = e, this.chunk = t3, this.nextLayer = n11, this.maxPoint = i2;
  }
  static create(e, t3, n11, i2) {
    return new s17(e, t3, n11, i2);
  }
  get length() {
    let e = this.chunk.length - 1;
    return e < 0 ? 0 : Math.max(this.chunkEnd(e), this.nextLayer.length);
  }
  get size() {
    if (this.isEmpty) return 0;
    let e = this.nextLayer.size;
    for (let t3 of this.chunk) e += t3.value.length;
    return e;
  }
  chunkEnd(e) {
    return this.chunkPos[e] + this.chunk[e].length;
  }
  update(e) {
    let { add: t3 = [], sort: n11 = false, filterFrom: i2 = 0, filterTo: r2 = this.length } = e, l9 = e.filter;
    if (t3.length == 0 && !l9) return this;
    if (n11 && (t3 = t3.slice().sort(ve)), this.isEmpty) return t3.length ? s17.of(t3) : this;
    let h = new re(this, null, -1).goto(0), o3 = 0, a2 = [], f = new se();
    for (; h.value || o3 < t3.length; ) if (o3 < t3.length && (h.from - t3[o3].from || h.startSide - t3[o3].value.startSide) >= 0) {
      let u2 = t3[o3++];
      f.addInner(u2.from, u2.to, u2.value) || a2.push(u2);
    } else h.rangeIndex == 1 && h.chunkIndex < this.chunk.length && (o3 == t3.length || this.chunkEnd(h.chunkIndex) < t3[o3].from) && (!l9 || i2 > this.chunkEnd(h.chunkIndex) || r2 < this.chunkPos[h.chunkIndex]) && f.addChunk(this.chunkPos[h.chunkIndex], this.chunk[h.chunkIndex]) ? h.nextChunk() : ((!l9 || i2 > h.to || r2 < h.from || l9(h.from, h.to, h.value)) && (f.addInner(h.from, h.to, h.value) || a2.push(j.create(h.from, h.to, h.value))), h.next());
    return f.finishInner(this.nextLayer.isEmpty && !a2.length ? s17.empty : this.nextLayer.update({
      add: a2,
      filter: l9,
      filterFrom: i2,
      filterTo: r2
    }));
  }
  map(e) {
    if (e.empty || this.isEmpty) return this;
    let t3 = [], n11 = [], i2 = -1;
    for (let l9 = 0; l9 < this.chunk.length; l9++) {
      let h = this.chunkPos[l9], o3 = this.chunk[l9], a2 = e.touchesRange(h, h + o3.length);
      if (a2 === false) i2 = Math.max(i2, o3.maxPoint), t3.push(o3), n11.push(e.mapPos(h));
      else if (a2 === true) {
        let { mapped: f, pos: u2 } = o3.map(h, e);
        f && (i2 = Math.max(i2, f.maxPoint), t3.push(f), n11.push(u2));
      }
    }
    let r2 = this.nextLayer.map(e);
    return t3.length == 0 ? r2 : new s17(n11, t3, r2 || s17.empty, i2);
  }
  between(e, t3, n11) {
    if (!this.isEmpty) {
      for (let i2 = 0; i2 < this.chunk.length; i2++) {
        let r2 = this.chunkPos[i2], l9 = this.chunk[i2];
        if (t3 >= r2 && e <= r2 + l9.length && l9.between(r2, e - r2, t3 - r2, n11) === false) return;
      }
      this.nextLayer.between(e, t3, n11);
    }
  }
  iter(e = 0) {
    return H.from([
      this
    ]).goto(e);
  }
  get isEmpty() {
    return this.nextLayer == this;
  }
  static iter(e, t3 = 0) {
    return H.from(e).goto(t3);
  }
  static compare(e, t3, n11, i2, r2 = -1) {
    let l9 = e.filter((u2) => u2.maxPoint > 0 || !u2.isEmpty && u2.maxPoint >= r2), h = t3.filter((u2) => u2.maxPoint > 0 || !u2.isEmpty && u2.maxPoint >= r2), o3 = Te(l9, h, n11), a2 = new T(l9, o3, r2), f = new T(h, o3, r2);
    n11.iterGaps((u2, c3, d) => Re(a2, u2, f, c3, d, i2)), n11.empty && n11.length == 0 && Re(a2, 0, f, 0, 0, i2);
  }
  static eq(e, t3, n11 = 0, i2) {
    i2 == null && (i2 = 1e9);
    let r2 = e.filter((f) => !f.isEmpty && t3.indexOf(f) < 0), l9 = t3.filter((f) => !f.isEmpty && e.indexOf(f) < 0);
    if (r2.length != l9.length) return false;
    if (!r2.length) return true;
    let h = Te(r2, l9), o3 = new T(r2, h, 0).goto(n11), a2 = new T(l9, h, 0).goto(n11);
    for (; ; ) {
      if (o3.to != a2.to || !ke(o3.active, a2.active) || o3.point && (!a2.point || !o3.point.eq(a2.point))) return false;
      if (o3.to > i2) return true;
      o3.next(), a2.next();
    }
  }
  static spans(e, t3, n11, i2, r2 = -1) {
    let l9 = new T(e, null, r2).goto(t3), h = t3, o3 = l9.openStart;
    for (; ; ) {
      let a2 = Math.min(l9.to, n11);
      if (l9.point ? (i2.point(h, a2, l9.point, l9.activeForPoint(l9.to), o3, l9.pointRank), o3 = l9.openEnd(a2) + (l9.to > a2 ? 1 : 0)) : a2 > h && (i2.span(h, a2, l9.active, o3), o3 = l9.openEnd(a2)), l9.to > n11) break;
      h = l9.to, l9.next();
    }
    return o3;
  }
  static of(e, t3 = false) {
    let n11 = new se();
    for (let i2 of e instanceof j ? [
      e
    ] : t3 ? st(e) : e) n11.add(i2.from, i2.to, i2.value);
    return n11.finish();
  }
};
O.empty = new O([], [], null, -1);
function st(s45) {
  if (s45.length > 1) for (let e = s45[0], t3 = 1; t3 < s45.length; t3++) {
    let n11 = s45[t3];
    if (ve(e, n11) > 0) return s45.slice().sort(ve);
    e = n11;
  }
  return s45;
}
O.empty.nextLayer = O.empty;
var se = class s18 {
  constructor() {
    this.chunks = [], this.chunkPos = [], this.chunkStart = -1, this.last = null, this.lastFrom = -1e9, this.lastTo = -1e9, this.from = [], this.to = [], this.value = [], this.maxPoint = -1, this.setMaxPoint = -1, this.nextLayer = null;
  }
  finishChunk(e) {
    this.chunks.push(new xe(this.from, this.to, this.value, this.maxPoint)), this.chunkPos.push(this.chunkStart), this.chunkStart = -1, this.setMaxPoint = Math.max(this.setMaxPoint, this.maxPoint), this.maxPoint = -1, e && (this.from = [], this.to = [], this.value = []);
  }
  add(e, t3, n11) {
    this.addInner(e, t3, n11) || (this.nextLayer || (this.nextLayer = new s18())).add(e, t3, n11);
  }
  addInner(e, t3, n11) {
    let i2 = e - this.lastTo || n11.startSide - this.last.endSide;
    if (i2 <= 0 && (e - this.lastFrom || n11.startSide - this.last.startSide) < 0) throw new Error("Ranges must be added sorted by `from` position and `startSide`");
    return i2 < 0 ? false : (this.from.length == 250 && this.finishChunk(true), this.chunkStart < 0 && (this.chunkStart = e), this.from.push(e - this.chunkStart), this.to.push(t3 - this.chunkStart), this.last = n11, this.lastFrom = e, this.lastTo = t3, this.value.push(n11), n11.point && (this.maxPoint = Math.max(this.maxPoint, t3 - e)), true);
  }
  addChunk(e, t3) {
    if ((e - this.lastTo || t3.value[0].startSide - this.last.endSide) < 0) return false;
    this.from.length && this.finishChunk(true), this.setMaxPoint = Math.max(this.setMaxPoint, t3.maxPoint), this.chunks.push(t3), this.chunkPos.push(e);
    let n11 = t3.value.length - 1;
    return this.last = t3.value[n11], this.lastFrom = t3.from[n11] + e, this.lastTo = t3.to[n11] + e, true;
  }
  finish() {
    return this.finishInner(O.empty);
  }
  finishInner(e) {
    if (this.from.length && this.finishChunk(false), this.chunks.length == 0) return e;
    let t3 = O.create(this.chunkPos, this.chunks, this.nextLayer ? this.nextLayer.finishInner(e) : e, this.setMaxPoint);
    return this.from = null, t3;
  }
};
function Te(s45, e, t3) {
  let n11 = /* @__PURE__ */ new Map();
  for (let r2 of s45) for (let l9 = 0; l9 < r2.chunk.length; l9++) r2.chunk[l9].maxPoint <= 0 && n11.set(r2.chunk[l9], r2.chunkPos[l9]);
  let i2 = /* @__PURE__ */ new Set();
  for (let r2 of e) for (let l9 = 0; l9 < r2.chunk.length; l9++) {
    let h = n11.get(r2.chunk[l9]);
    h != null && (t3 ? t3.mapPos(h) : h) == r2.chunkPos[l9] && !t3?.touchesRange(h, h + r2.chunk[l9].length) && i2.add(r2.chunk[l9]);
  }
  return i2;
}
var re = class {
  constructor(e, t3, n11, i2 = 0) {
    this.layer = e, this.skip = t3, this.minPoint = n11, this.rank = i2;
  }
  get startSide() {
    return this.value ? this.value.startSide : 0;
  }
  get endSide() {
    return this.value ? this.value.endSide : 0;
  }
  goto(e, t3 = -1e9) {
    return this.chunkIndex = this.rangeIndex = 0, this.gotoInner(e, t3, false), this;
  }
  gotoInner(e, t3, n11) {
    for (; this.chunkIndex < this.layer.chunk.length; ) {
      let i2 = this.layer.chunk[this.chunkIndex];
      if (!(this.skip && this.skip.has(i2) || this.layer.chunkEnd(this.chunkIndex) < e || i2.maxPoint < this.minPoint)) break;
      this.chunkIndex++, n11 = false;
    }
    if (this.chunkIndex < this.layer.chunk.length) {
      let i2 = this.layer.chunk[this.chunkIndex].findIndex(e - this.layer.chunkPos[this.chunkIndex], t3, true);
      (!n11 || this.rangeIndex < i2) && this.setRangeIndex(i2);
    }
    this.next();
  }
  forward(e, t3) {
    (this.to - e || this.endSide - t3) < 0 && this.gotoInner(e, t3, true);
  }
  next() {
    for (; ; ) if (this.chunkIndex == this.layer.chunk.length) {
      this.from = this.to = 1e9, this.value = null;
      break;
    } else {
      let e = this.layer.chunkPos[this.chunkIndex], t3 = this.layer.chunk[this.chunkIndex], n11 = e + t3.from[this.rangeIndex];
      if (this.from = n11, this.to = e + t3.to[this.rangeIndex], this.value = t3.value[this.rangeIndex], this.setRangeIndex(this.rangeIndex + 1), this.minPoint < 0 || this.value.point && this.to - this.from >= this.minPoint) break;
    }
  }
  setRangeIndex(e) {
    if (e == this.layer.chunk[this.chunkIndex].value.length) {
      if (this.chunkIndex++, this.skip) for (; this.chunkIndex < this.layer.chunk.length && this.skip.has(this.layer.chunk[this.chunkIndex]); ) this.chunkIndex++;
      this.rangeIndex = 0;
    } else this.rangeIndex = e;
  }
  nextChunk() {
    this.chunkIndex++, this.rangeIndex = 0, this.next();
  }
  compare(e) {
    return this.from - e.from || this.startSide - e.startSide || this.rank - e.rank || this.to - e.to || this.endSide - e.endSide;
  }
};
var H = class s19 {
  constructor(e) {
    this.heap = e;
  }
  static from(e, t3 = null, n11 = -1) {
    let i2 = [];
    for (let r2 = 0; r2 < e.length; r2++) for (let l9 = e[r2]; !l9.isEmpty; l9 = l9.nextLayer) l9.maxPoint >= n11 && i2.push(new re(l9, t3, n11, r2));
    return i2.length == 1 ? i2[0] : new s19(i2);
  }
  get startSide() {
    return this.value ? this.value.startSide : 0;
  }
  goto(e, t3 = -1e9) {
    for (let n11 of this.heap) n11.goto(e, t3);
    for (let n11 = this.heap.length >> 1; n11 >= 0; n11--) oe(this.heap, n11);
    return this.next(), this;
  }
  forward(e, t3) {
    for (let n11 of this.heap) n11.forward(e, t3);
    for (let n11 = this.heap.length >> 1; n11 >= 0; n11--) oe(this.heap, n11);
    (this.to - e || this.value.endSide - t3) < 0 && this.next();
  }
  next() {
    if (this.heap.length == 0) this.from = this.to = 1e9, this.value = null, this.rank = -1;
    else {
      let e = this.heap[0];
      this.from = e.from, this.to = e.to, this.value = e.value, this.rank = e.rank, e.value && e.next(), oe(this.heap, 0);
    }
  }
};
function oe(s45, e) {
  for (let t3 = s45[e]; ; ) {
    let n11 = (e << 1) + 1;
    if (n11 >= s45.length) break;
    let i2 = s45[n11];
    if (n11 + 1 < s45.length && i2.compare(s45[n11 + 1]) >= 0 && (i2 = s45[n11 + 1], n11++), t3.compare(i2) < 0) break;
    s45[n11] = t3, s45[e] = i2, e = n11;
  }
}
var T = class {
  constructor(e, t3, n11) {
    this.minPoint = n11, this.active = [], this.activeTo = [], this.activeRank = [], this.minActive = -1, this.point = null, this.pointFrom = 0, this.pointRank = 0, this.to = -1e9, this.endSide = 0, this.openStart = -1, this.cursor = H.from(e, t3, n11);
  }
  goto(e, t3 = -1e9) {
    return this.cursor.goto(e, t3), this.active.length = this.activeTo.length = this.activeRank.length = 0, this.minActive = -1, this.to = e, this.endSide = t3, this.openStart = -1, this.next(), this;
  }
  forward(e, t3) {
    for (; this.minActive > -1 && (this.activeTo[this.minActive] - e || this.active[this.minActive].endSide - t3) < 0; ) this.removeActive(this.minActive);
    this.cursor.forward(e, t3);
  }
  removeActive(e) {
    Z(this.active, e), Z(this.activeTo, e), Z(this.activeRank, e), this.minActive = Be(this.active, this.activeTo);
  }
  addActive(e) {
    let t3 = 0, { value: n11, to: i2, rank: r2 } = this.cursor;
    for (; t3 < this.activeRank.length && this.activeRank[t3] <= r2; ) t3++;
    K(this.active, t3, n11), K(this.activeTo, t3, i2), K(this.activeRank, t3, r2), e && K(e, t3, this.cursor.from), this.minActive = Be(this.active, this.activeTo);
  }
  next() {
    let e = this.to, t3 = this.point;
    this.point = null;
    let n11 = this.openStart < 0 ? [] : null, i2 = 0;
    for (; ; ) {
      let r2 = this.minActive;
      if (r2 > -1 && (this.activeTo[r2] - this.cursor.from || this.active[r2].endSide - this.cursor.startSide) < 0) {
        if (this.activeTo[r2] > e) {
          this.to = this.activeTo[r2], this.endSide = this.active[r2].endSide;
          break;
        }
        this.removeActive(r2), n11 && Z(n11, r2);
      } else if (this.cursor.value) if (this.cursor.from > e) {
        this.to = this.cursor.from, this.endSide = this.cursor.startSide;
        break;
      } else {
        let l9 = this.cursor.value;
        if (!l9.point) this.addActive(n11), this.cursor.next();
        else if (t3 && this.cursor.to == this.to && this.cursor.from < this.cursor.to) this.cursor.next();
        else {
          this.point = l9, this.pointFrom = this.cursor.from, this.pointRank = this.cursor.rank, this.to = this.cursor.to, this.endSide = l9.endSide, this.cursor.from < e && (i2 = 1), this.cursor.next(), this.forward(this.to, this.endSide);
          break;
        }
      }
      else {
        this.to = this.endSide = 1e9;
        break;
      }
    }
    if (n11) {
      let r2 = 0;
      for (; r2 < n11.length && n11[r2] < e; ) r2++;
      this.openStart = r2 + i2;
    }
  }
  activeForPoint(e) {
    if (!this.active.length) return this.active;
    let t3 = [];
    for (let n11 = this.active.length - 1; n11 >= 0 && !(this.activeRank[n11] < this.pointRank); n11--) (this.activeTo[n11] > e || this.activeTo[n11] == e && this.active[n11].endSide >= this.point.endSide) && t3.push(this.active[n11]);
    return t3.reverse();
  }
  openEnd(e) {
    let t3 = 0;
    for (let n11 = this.activeTo.length - 1; n11 >= 0 && this.activeTo[n11] > e; n11--) t3++;
    return t3;
  }
};
function Re(s45, e, t3, n11, i2, r2) {
  s45.goto(e), t3.goto(n11);
  let l9 = n11 + i2, h = n11, o3 = n11 - e;
  for (; ; ) {
    let a2 = s45.to + o3 - t3.to || s45.endSide - t3.endSide, f = a2 < 0 ? s45.to + o3 : t3.to, u2 = Math.min(f, l9);
    if (s45.point || t3.point ? s45.point && t3.point && (s45.point == t3.point || s45.point.eq(t3.point)) && ke(s45.activeForPoint(s45.to + o3), t3.activeForPoint(t3.to)) || r2.comparePoint(h, u2, s45.point, t3.point) : u2 > h && !ke(s45.active, t3.active) && r2.compareRange(h, u2, s45.active, t3.active), f > l9) break;
    h = f, a2 <= 0 && s45.next(), a2 >= 0 && t3.next();
  }
}
function ke(s45, e) {
  if (s45.length != e.length) return false;
  for (let t3 = 0; t3 < s45.length; t3++) if (s45[t3] != e[t3] && !s45[t3].eq(e[t3])) return false;
  return true;
}
function Z(s45, e) {
  for (let t3 = e, n11 = s45.length - 1; t3 < n11; t3++) s45[t3] = s45[t3 + 1];
  s45.pop();
}
function K(s45, e, t3) {
  for (let n11 = s45.length - 1; n11 >= e; n11--) s45[n11 + 1] = s45[n11];
  s45[e] = t3;
}
function Be(s45, e) {
  let t3 = -1, n11 = 1e9;
  for (let i2 = 0; i2 < e.length; i2++) (e[i2] - n11 || s45[i2].endSide - s45[t3].endSide) < 0 && (t3 = i2, n11 = e[i2]);
  return t3;
}
function at(s45, e, t3, n11) {
  for (let i2 = 0, r2 = 0; ; ) {
    if (r2 >= e) return i2;
    if (i2 == s45.length) break;
    r2 += s45.charCodeAt(i2) == 9 ? t3 - r2 % t3 : 1, i2 = _(s45, i2);
  }
  return n11 === true ? -1 : s45.length;
}

// deno:https://esm.sh/style-mod@4.1.3/denonext/style-mod.mjs
var m2 = typeof Symbol > "u" ? "__\u037C" : Symbol.for("\u037C");
var c = typeof Symbol > "u" ? "__styleSet" + Math.floor(Math.random() * 1e8) : Symbol("styleSet");
var w2 = typeof globalThis < "u" || typeof globalThis < "u" ? globalThis : {};
var T2 = class {
  constructor(e, i2) {
    this.rules = [];
    let { finish: l9 } = i2 || {};
    function n11(t3) {
      return /^@/.test(t3) ? [
        t3
      ] : t3.split(/,\s*/);
    }
    function s45(t3, a2, h, f) {
      let p2 = [], u2 = /^@(\w+)\b/.exec(t3[0]), g3 = u2 && u2[1] == "keyframes";
      if (u2 && a2 == null) return h.push(t3[0] + ";");
      for (let o3 in a2) {
        let r2 = a2[o3];
        if (/&/.test(o3)) s45(o3.split(/,\s*/).map((d) => t3.map((y4) => d.replace(/&/g, y4))).reduce((d, y4) => d.concat(y4)), r2, h);
        else if (r2 && typeof r2 == "object") {
          if (!u2) throw new RangeError("The value of a property (" + o3 + ") should be a primitive value.");
          s45(n11(o3), r2, p2, g3);
        } else r2 != null && p2.push(o3.replace(/_.*/, "").replace(/[A-Z]/g, (d) => "-" + d.toLowerCase()) + ": " + r2 + ";");
      }
      (p2.length || g3) && h.push((l9 && !u2 && !f ? t3.map(l9) : t3).join(", ") + " {" + p2.join(" ") + "}");
    }
    for (let t3 in e) s45(n11(t3), e[t3], this.rules);
  }
  getRules() {
    return this.rules.join(`
`);
  }
  static newName() {
    let e = w2[m2] || 1;
    return w2[m2] = e + 1, "\u037C" + e.toString(36);
  }
  static mount(e, i2, l9) {
    let n11 = e[c], s45 = l9 && l9.nonce;
    n11 ? s45 && n11.setNonce(s45) : n11 = new S2(e, s45), n11.mount(Array.isArray(i2) ? i2 : [
      i2
    ], e);
  }
};
var b2 = /* @__PURE__ */ new Map();
var S2 = class {
  constructor(e, i2) {
    let l9 = e.ownerDocument || e, n11 = l9.defaultView;
    if (!e.head && e.adoptedStyleSheets && n11.CSSStyleSheet) {
      let s45 = b2.get(l9);
      if (s45) return e[c] = s45;
      this.sheet = new n11.CSSStyleSheet(), b2.set(l9, this);
    } else this.styleTag = l9.createElement("style"), i2 && this.styleTag.setAttribute("nonce", i2);
    this.modules = [], e[c] = this;
  }
  mount(e, i2) {
    let l9 = this.sheet, n11 = 0, s45 = 0;
    for (let t3 = 0; t3 < e.length; t3++) {
      let a2 = e[t3], h = this.modules.indexOf(a2);
      if (h < s45 && h > -1 && (this.modules.splice(h, 1), s45--, h = -1), h == -1) {
        if (this.modules.splice(s45++, 0, a2), l9) for (let f = 0; f < a2.rules.length; f++) l9.insertRule(a2.rules[f], n11++);
      } else {
        for (; s45 < h; ) n11 += this.modules[s45++].rules.length;
        n11 += a2.rules.length, s45++;
      }
    }
    if (l9) i2.adoptedStyleSheets.indexOf(this.sheet) < 0 && (i2.adoptedStyleSheets = [
      this.sheet,
      ...i2.adoptedStyleSheets
    ]);
    else {
      let t3 = "";
      for (let h = 0; h < this.modules.length; h++) t3 += this.modules[h].getRules() + `
`;
      this.styleTag.textContent = t3;
      let a2 = i2.head || i2;
      this.styleTag.parentNode != a2 && a2.insertBefore(this.styleTag, a2.firstChild);
    }
  }
  setNonce(e) {
    this.styleTag && this.styleTag.getAttribute("nonce") != e && this.styleTag.setAttribute("nonce", e);
  }
};

// deno:https://esm.sh/w3c-keyname@2.2.8/denonext/w3c-keyname.mjs
var t = {
  8: "Backspace",
  9: "Tab",
  10: "Enter",
  12: "NumLock",
  13: "Enter",
  16: "Shift",
  17: "Control",
  18: "Alt",
  20: "CapsLock",
  27: "Escape",
  32: " ",
  33: "PageUp",
  34: "PageDown",
  35: "End",
  36: "Home",
  37: "ArrowLeft",
  38: "ArrowUp",
  39: "ArrowRight",
  40: "ArrowDown",
  44: "PrintScreen",
  45: "Insert",
  46: "Delete",
  59: ";",
  61: "=",
  91: "Meta",
  92: "Meta",
  106: "*",
  107: "+",
  108: ",",
  109: "-",
  110: ".",
  111: "/",
  144: "NumLock",
  145: "ScrollLock",
  160: "Shift",
  161: "Shift",
  162: "Control",
  163: "Control",
  164: "Alt",
  165: "Alt",
  173: "-",
  186: ";",
  187: "=",
  188: ",",
  189: "-",
  190: ".",
  191: "/",
  192: "`",
  219: "[",
  220: "\\",
  221: "]",
  222: "'"
};
var i = {
  48: ")",
  49: "!",
  50: "@",
  51: "#",
  52: "$",
  53: "%",
  54: "^",
  55: "&",
  56: "*",
  57: "(",
  59: ":",
  61: "+",
  173: "_",
  186: ":",
  187: "+",
  188: "<",
  189: "_",
  190: ">",
  191: "?",
  192: "~",
  219: "{",
  220: "|",
  221: "}",
  222: '"'
};
var n = typeof navigator < "u" && /Mac/.test(navigator.platform);
var y2 = typeof navigator < "u" && /MSIE \d|Trident\/(?:[7-9]|\d{2,})\..*rv:(\d+)/.exec(navigator.userAgent);
for (r = 0; r < 10; r++) t[48 + r] = t[96 + r] = String(r);
var r;
for (r = 1; r <= 24; r++) t[r + 111] = "F" + r;
var r;
for (r = 65; r <= 90; r++) t[r] = String.fromCharCode(r + 32), i[r] = String.fromCharCode(r);
var r;
for (a in t) i.hasOwnProperty(a) || (i[a] = t[a]);
var a;
function g(o3) {
  var f = n && o3.metaKey && o3.shiftKey && !o3.ctrlKey && !o3.altKey || y2 && o3.shiftKey && o3.key && o3.key.length == 1 || o3.key == "Unidentified", e = !f && o3.key || (o3.shiftKey ? i : t)[o3.keyCode] || o3.key || "Unidentified";
  return e == "Esc" && (e = "Escape"), e == "Del" && (e = "Delete"), e == "Left" && (e = "ArrowLeft"), e == "Up" && (e = "ArrowUp"), e == "Right" && (e = "ArrowRight"), e == "Down" && (e = "ArrowDown"), e;
}

// deno:https://esm.sh/@codemirror/view@0.20.7/denonext/view.mjs
function Yt(s45) {
  let t3;
  return s45.nodeType == 11 ? t3 = s45.getSelection ? s45 : s45.ownerDocument : t3 = s45, t3.getSelection();
}
function pt(s45, t3) {
  return t3 ? s45 == t3 || s45.contains(t3.nodeType != 1 ? t3.parentNode : t3) : false;
}
function gn() {
  let s45 = document.activeElement;
  for (; s45 && s45.shadowRoot; ) s45 = s45.shadowRoot.activeElement;
  return s45;
}
function De2(s45, t3) {
  if (!t3.anchorNode) return false;
  try {
    return pt(s45, t3.anchorNode);
  } catch {
    return false;
  }
}
function Tt(s45) {
  return s45.nodeType == 3 ? Ot(s45, 0, s45.nodeValue.length).getClientRects() : s45.nodeType == 1 ? s45.getClientRects() : [];
}
function Ut(s45, t3, e, i2) {
  return e ? xi(s45, t3, e, i2, -1) || xi(s45, t3, e, i2, 1) : false;
}
function Te2(s45) {
  for (var t3 = 0; ; t3++) if (s45 = s45.previousSibling, !s45) return t3;
}
function xi(s45, t3, e, i2, n11) {
  for (; ; ) {
    if (s45 == e && t3 == i2) return true;
    if (t3 == (n11 < 0 ? 0 : Xt(s45))) {
      if (s45.nodeName == "DIV") return false;
      let r2 = s45.parentNode;
      if (!r2 || r2.nodeType != 1) return false;
      t3 = Te2(s45) + (n11 < 0 ? 0 : 1), s45 = r2;
    } else if (s45.nodeType == 1) {
      if (s45 = s45.childNodes[t3 + (n11 < 0 ? -1 : 0)], s45.nodeType == 1 && s45.contentEditable == "false") return false;
      t3 = n11 < 0 ? Xt(s45) : 0;
    } else return false;
  }
}
function Xt(s45) {
  return s45.nodeType == 3 ? s45.nodeValue.length : s45.childNodes.length;
}
var ds = {
  left: 0,
  right: 0,
  top: 0,
  bottom: 0
};
function ge2(s45, t3) {
  let e = t3 ? s45.left : s45.right;
  return {
    left: e,
    right: e,
    top: s45.top,
    bottom: s45.bottom
  };
}
function bn(s45) {
  return {
    left: 0,
    right: s45.innerWidth,
    top: 0,
    bottom: s45.innerHeight
  };
}
function yn(s45, t3, e, i2, n11, r2, o3, l9) {
  let h = s45.ownerDocument, a2 = h.defaultView;
  for (let c3 = s45; c3; ) if (c3.nodeType == 1) {
    let f, u2 = c3 == h.body;
    if (u2) f = bn(a2);
    else {
      if (c3.scrollHeight <= c3.clientHeight && c3.scrollWidth <= c3.clientWidth) {
        c3 = c3.parentNode;
        continue;
      }
      let m4 = c3.getBoundingClientRect();
      f = {
        left: m4.left,
        right: m4.left + c3.clientWidth,
        top: m4.top,
        bottom: m4.top + c3.clientHeight
      };
    }
    let d = 0, p2 = 0;
    if (n11 == "nearest") t3.top < f.top ? (p2 = -(f.top - t3.top + o3), e > 0 && t3.bottom > f.bottom + p2 && (p2 = t3.bottom - f.bottom + p2 + o3)) : t3.bottom > f.bottom && (p2 = t3.bottom - f.bottom + o3, e < 0 && t3.top - p2 < f.top && (p2 = -(f.top + p2 - t3.top + o3)));
    else {
      let m4 = t3.bottom - t3.top, b4 = f.bottom - f.top;
      p2 = (n11 == "center" && m4 <= b4 ? t3.top + m4 / 2 - b4 / 2 : n11 == "start" || n11 == "center" && e < 0 ? t3.top - o3 : t3.bottom - b4 + o3) - f.top;
    }
    if (i2 == "nearest" ? t3.left < f.left ? (d = -(f.left - t3.left + r2), e > 0 && t3.right > f.right + d && (d = t3.right - f.right + d + r2)) : t3.right > f.right && (d = t3.right - f.right + r2, e < 0 && t3.left < f.left + d && (d = -(f.left + d - t3.left + r2))) : d = (i2 == "center" ? t3.left + (t3.right - t3.left) / 2 - (f.right - f.left) / 2 : i2 == "start" == l9 ? t3.left - r2 : t3.right - (f.right - f.left) + r2) - f.left, d || p2) if (u2) a2.scrollBy(d, p2);
    else {
      if (p2) {
        let m4 = c3.scrollTop;
        c3.scrollTop += p2, p2 = c3.scrollTop - m4;
      }
      if (d) {
        let m4 = c3.scrollLeft;
        c3.scrollLeft += d, d = c3.scrollLeft - m4;
      }
      t3 = {
        left: t3.left - d,
        top: t3.top - p2,
        right: t3.right - d,
        bottom: t3.bottom - p2
      };
    }
    if (u2) break;
    c3 = c3.assignedSlot || c3.parentNode, i2 = n11 = "nearest";
  } else if (c3.nodeType == 11) c3 = c3.host;
  else break;
}
var Oe2 = class {
  constructor() {
    this.anchorNode = null, this.anchorOffset = 0, this.focusNode = null, this.focusOffset = 0;
  }
  eq(t3) {
    return this.anchorNode == t3.anchorNode && this.anchorOffset == t3.anchorOffset && this.focusNode == t3.focusNode && this.focusOffset == t3.focusOffset;
  }
  setRange(t3) {
    this.set(t3.anchorNode, t3.anchorOffset, t3.focusNode, t3.focusOffset);
  }
  set(t3, e, i2, n11) {
    this.anchorNode = t3, this.anchorOffset = e, this.focusNode = i2, this.focusOffset = n11;
  }
};
var ht2 = null;
function us(s45) {
  if (s45.setActive) return s45.setActive();
  if (ht2) return s45.focus(ht2);
  let t3 = [];
  for (let e = s45; e && (t3.push(e, e.scrollTop, e.scrollLeft), e != e.ownerDocument); e = e.parentNode) ;
  if (s45.focus(ht2 == null ? {
    get preventScroll() {
      return ht2 = {
        preventScroll: true
      }, true;
    }
  } : void 0), !ht2) {
    ht2 = false;
    for (let e = 0; e < t3.length; ) {
      let i2 = t3[e++], n11 = t3[e++], r2 = t3[e++];
      i2.scrollTop != n11 && (i2.scrollTop = n11), i2.scrollLeft != r2 && (i2.scrollLeft = r2);
    }
  }
}
var Si;
function Ot(s45, t3, e = t3) {
  let i2 = Si || (Si = document.createRange());
  return i2.setEnd(s45, e), i2.setStart(s45, t3), i2;
}
function Ct(s45, t3, e) {
  let i2 = {
    key: t3,
    code: t3,
    keyCode: e,
    which: e,
    cancelable: true
  }, n11 = new KeyboardEvent("keydown", i2);
  n11.synthetic = true, s45.dispatchEvent(n11);
  let r2 = new KeyboardEvent("keyup", i2);
  return r2.synthetic = true, s45.dispatchEvent(r2), n11.defaultPrevented || r2.defaultPrevented;
}
function wn(s45) {
  for (; s45; ) {
    if (s45 && (s45.nodeType == 9 || s45.nodeType == 11 && s45.host)) return s45;
    s45 = s45.assignedSlot || s45.parentNode;
  }
  return null;
}
function ps(s45) {
  for (; s45.attributes.length; ) s45.removeAttributeNode(s45.attributes[0]);
}
var B2 = class s20 {
  constructor(t3, e, i2 = true) {
    this.node = t3, this.offset = e, this.precise = i2;
  }
  static before(t3, e) {
    return new s20(t3.parentNode, Te2(t3), e);
  }
  static after(t3, e) {
    return new s20(t3.parentNode, Te2(t3) + 1, e);
  }
};
var mi = [];
var R2 = class s21 {
  constructor() {
    this.parent = null, this.dom = null, this.dirty = 2;
  }
  get editorView() {
    if (!this.parent) throw new Error("Accessing view in orphan content view");
    return this.parent.editorView;
  }
  get overrideDOMText() {
    return null;
  }
  get posAtStart() {
    return this.parent ? this.parent.posBefore(this) : 0;
  }
  get posAtEnd() {
    return this.posAtStart + this.length;
  }
  posBefore(t3) {
    let e = this.posAtStart;
    for (let i2 of this.children) {
      if (i2 == t3) return e;
      e += i2.length + i2.breakAfter;
    }
    throw new RangeError("Invalid child in posBefore");
  }
  posAfter(t3) {
    return this.posBefore(t3) + t3.length;
  }
  coordsAt(t3, e) {
    return null;
  }
  sync(t3) {
    if (this.dirty & 2) {
      let e = this.dom, i2 = null, n11;
      for (let r2 of this.children) {
        if (r2.dirty) {
          if (!r2.dom && (n11 = i2 ? i2.nextSibling : e.firstChild)) {
            let o3 = s21.get(n11);
            (!o3 || !o3.parent && o3.constructor == r2.constructor) && r2.reuseDOM(n11);
          }
          r2.sync(t3), r2.dirty = 0;
        }
        if (n11 = i2 ? i2.nextSibling : e.firstChild, t3 && !t3.written && t3.node == e && n11 != r2.dom && (t3.written = true), r2.dom.parentNode == e) for (; n11 && n11 != r2.dom; ) n11 = Ci(n11);
        else e.insertBefore(r2.dom, n11);
        i2 = r2.dom;
      }
      for (n11 = i2 ? i2.nextSibling : e.firstChild, n11 && t3 && t3.node == e && (t3.written = true); n11; ) n11 = Ci(n11);
    } else if (this.dirty & 1) for (let e of this.children) e.dirty && (e.sync(t3), e.dirty = 0);
  }
  reuseDOM(t3) {
  }
  localPosFromDOM(t3, e) {
    let i2;
    if (t3 == this.dom) i2 = this.dom.childNodes[e];
    else {
      let n11 = Xt(t3) == 0 ? 0 : e == 0 ? -1 : 1;
      for (; ; ) {
        let r2 = t3.parentNode;
        if (r2 == this.dom) break;
        n11 == 0 && r2.firstChild != r2.lastChild && (t3 == r2.firstChild ? n11 = -1 : n11 = 1), t3 = r2;
      }
      n11 < 0 ? i2 = t3 : i2 = t3.nextSibling;
    }
    if (i2 == this.dom.firstChild) return 0;
    for (; i2 && !s21.get(i2); ) i2 = i2.nextSibling;
    if (!i2) return this.length;
    for (let n11 = 0, r2 = 0; ; n11++) {
      let o3 = this.children[n11];
      if (o3.dom == i2) return r2;
      r2 += o3.length + o3.breakAfter;
    }
  }
  domBoundsAround(t3, e, i2 = 0) {
    let n11 = -1, r2 = -1, o3 = -1, l9 = -1;
    for (let h = 0, a2 = i2, c3 = i2; h < this.children.length; h++) {
      let f = this.children[h], u2 = a2 + f.length;
      if (a2 < t3 && u2 > e) return f.domBoundsAround(t3, e, a2);
      if (u2 >= t3 && n11 == -1 && (n11 = h, r2 = a2), a2 > e && f.dom.parentNode == this.dom) {
        o3 = h, l9 = c3;
        break;
      }
      c3 = u2, a2 = u2 + f.breakAfter;
    }
    return {
      from: r2,
      to: l9 < 0 ? i2 + this.length : l9,
      startDOM: (n11 ? this.children[n11 - 1].dom.nextSibling : null) || this.dom.firstChild,
      endDOM: o3 < this.children.length && o3 >= 0 ? this.children[o3].dom : null
    };
  }
  markDirty(t3 = false) {
    this.dirty |= 2, this.markParentsDirty(t3);
  }
  markParentsDirty(t3) {
    for (let e = this.parent; e; e = e.parent) {
      if (t3 && (e.dirty |= 2), e.dirty & 1) return;
      e.dirty |= 1, t3 = false;
    }
  }
  setParent(t3) {
    this.parent != t3 && (this.parent = t3, this.dirty && this.markParentsDirty(true));
  }
  setDOM(t3) {
    this.dom && (this.dom.cmView = null), this.dom = t3, t3.cmView = this;
  }
  get rootView() {
    for (let t3 = this; ; ) {
      let e = t3.parent;
      if (!e) return t3;
      t3 = e;
    }
  }
  replaceChildren(t3, e, i2 = mi) {
    this.markDirty();
    for (let n11 = t3; n11 < e; n11++) {
      let r2 = this.children[n11];
      r2.parent == this && r2.destroy();
    }
    this.children.splice(t3, e - t3, ...i2);
    for (let n11 = 0; n11 < i2.length; n11++) i2[n11].setParent(this);
  }
  ignoreMutation(t3) {
    return false;
  }
  ignoreEvent(t3) {
    return false;
  }
  childCursor(t3 = this.length) {
    return new Jt(this.children, t3, this.children.length);
  }
  childPos(t3, e = 1) {
    return this.childCursor().findPos(t3, e);
  }
  toString() {
    let t3 = this.constructor.name.replace("View", "");
    return t3 + (this.children.length ? "(" + this.children.join() + ")" : this.length ? "[" + (t3 == "Text" ? this.text : this.length) + "]" : "") + (this.breakAfter ? "#" : "");
  }
  static get(t3) {
    return t3.cmView;
  }
  get isEditable() {
    return true;
  }
  merge(t3, e, i2, n11, r2, o3) {
    return false;
  }
  become(t3) {
    return false;
  }
  getSide() {
    return 0;
  }
  destroy() {
    this.parent = null;
  }
};
R2.prototype.breakAfter = 0;
function Ci(s45) {
  let t3 = s45.nextSibling;
  return s45.parentNode.removeChild(s45), t3;
}
var Jt = class {
  constructor(t3, e, i2) {
    this.children = t3, this.pos = e, this.i = i2, this.off = 0;
  }
  findPos(t3, e = 1) {
    for (; ; ) {
      if (t3 > this.pos || t3 == this.pos && (e > 0 || this.i == 0 || this.children[this.i - 1].breakAfter)) return this.off = t3 - this.pos, this;
      let i2 = this.children[--this.i];
      this.pos -= i2.length + i2.breakAfter;
    }
  }
};
function ms(s45, t3, e, i2, n11, r2, o3, l9, h) {
  let { children: a2 } = s45, c3 = a2.length ? a2[t3] : null, f = r2.length ? r2[r2.length - 1] : null, u2 = f ? f.breakAfter : o3;
  if (!(t3 == i2 && c3 && !o3 && !u2 && r2.length < 2 && c3.merge(e, n11, r2.length ? f : null, e == 0, l9, h))) {
    if (i2 < a2.length) {
      let d = a2[i2];
      d && n11 < d.length ? (t3 == i2 && (d = d.split(n11), n11 = 0), !u2 && f && d.merge(0, n11, f, true, 0, h) ? r2[r2.length - 1] = d : (n11 && d.merge(0, n11, null, false, 0, h), r2.push(d))) : d?.breakAfter && (f ? f.breakAfter = 1 : o3 = 1), i2++;
    }
    for (c3 && (c3.breakAfter = o3, e > 0 && (!o3 && r2.length && c3.merge(e, c3.length, r2[0], false, l9, 0) ? c3.breakAfter = r2.shift().breakAfter : (e < c3.length || c3.children.length && c3.children[c3.children.length - 1].length == 0) && c3.merge(e, c3.length, null, false, l9, 0), t3++)); t3 < i2 && r2.length; ) if (a2[i2 - 1].become(r2[r2.length - 1])) i2--, r2.pop(), h = r2.length ? 0 : l9;
    else if (a2[t3].become(r2[0])) t3++, r2.shift(), l9 = r2.length ? 0 : h;
    else break;
    !r2.length && t3 && i2 < a2.length && !a2[t3 - 1].breakAfter && a2[i2].merge(0, 0, a2[t3 - 1], false, l9, h) && t3--, (t3 < i2 || r2.length) && s45.replaceChildren(t3, i2, r2);
  }
}
function gs(s45, t3, e, i2, n11, r2) {
  let o3 = s45.childCursor(), { i: l9, off: h } = o3.findPos(e, 1), { i: a2, off: c3 } = o3.findPos(t3, -1), f = t3 - e;
  for (let u2 of i2) f += u2.length;
  s45.length += f, ms(s45, a2, c3, l9, h, i2, 0, n11, r2);
}
var V2 = typeof navigator < "u" ? navigator : {
  userAgent: "",
  vendor: "",
  platform: ""
};
var Re2 = typeof document < "u" ? document : {
  documentElement: {
    style: {}
  }
};
var Le2 = /Edge\/(\d+)/.exec(V2.userAgent);
var bs = /MSIE \d/.test(V2.userAgent);
var Ee2 = /Trident\/(?:[7-9]|\d{2,})\..*rv:(\d+)/.exec(V2.userAgent);
var be2 = !!(bs || Ee2 || Le2);
var Mi = !be2 && /gecko\/(\d+)/i.test(V2.userAgent);
var ye2 = !be2 && /Chrome\/(\d+)/.exec(V2.userAgent);
var ki = "webkitFontSmoothing" in Re2.documentElement.style;
var ys = !be2 && /Apple Computer/.test(V2.vendor);
var Ai = ys && (/Mobile\/\w+/.test(V2.userAgent) || V2.maxTouchPoints > 2);
var g2 = {
  mac: Ai || /Mac/.test(V2.platform),
  windows: /Win/.test(V2.platform),
  linux: /Linux|X11/.test(V2.platform),
  ie: be2,
  ie_version: bs ? Re2.documentMode || 6 : Ee2 ? +Ee2[1] : Le2 ? +Le2[1] : 0,
  gecko: Mi,
  gecko_version: Mi ? +(/Firefox\/(\d+)/.exec(V2.userAgent) || [
    0,
    0
  ])[1] : 0,
  chrome: !!ye2,
  chrome_version: ye2 ? +ye2[1] : 0,
  ios: Ai,
  android: /Android\b/.test(V2.userAgent),
  webkit: ki,
  safari: ys,
  webkit_version: ki ? +(/\bAppleWebKit\/(\d+)/.exec(navigator.userAgent) || [
    0,
    0
  ])[1] : 0,
  tabSize: Re2.documentElement.style.tabSize != null ? "tab-size" : "-moz-tab-size"
};
var vn = 256;
var rt2 = class s22 extends R2 {
  constructor(t3) {
    super(), this.text = t3;
  }
  get length() {
    return this.text.length;
  }
  createDOM(t3) {
    this.setDOM(t3 || document.createTextNode(this.text));
  }
  sync(t3) {
    this.dom || this.createDOM(), this.dom.nodeValue != this.text && (t3 && t3.node == this.dom && (t3.written = true), this.dom.nodeValue = this.text);
  }
  reuseDOM(t3) {
    t3.nodeType == 3 && this.createDOM(t3);
  }
  merge(t3, e, i2) {
    return i2 && (!(i2 instanceof s22) || this.length - (e - t3) + i2.length > vn) ? false : (this.text = this.text.slice(0, t3) + (i2 ? i2.text : "") + this.text.slice(e), this.markDirty(), true);
  }
  split(t3) {
    let e = new s22(this.text.slice(t3));
    return this.text = this.text.slice(0, t3), this.markDirty(), e;
  }
  localPosFromDOM(t3, e) {
    return t3 == this.dom ? e : e ? this.text.length : 0;
  }
  domAtPos(t3) {
    return new B2(this.dom, t3);
  }
  domBoundsAround(t3, e, i2) {
    return {
      from: i2,
      to: i2 + this.length,
      startDOM: this.dom,
      endDOM: this.dom.nextSibling
    };
  }
  coordsAt(t3, e) {
    return Be2(this.dom, t3, e);
  }
};
var q2 = class s23 extends R2 {
  constructor(t3, e = [], i2 = 0) {
    super(), this.mark = t3, this.children = e, this.length = i2;
    for (let n11 of e) n11.setParent(this);
  }
  setAttrs(t3) {
    if (ps(t3), this.mark.class && (t3.className = this.mark.class), this.mark.attrs) for (let e in this.mark.attrs) t3.setAttribute(e, this.mark.attrs[e]);
    return t3;
  }
  reuseDOM(t3) {
    t3.nodeName == this.mark.tagName.toUpperCase() && (this.setDOM(t3), this.dirty |= 6);
  }
  sync(t3) {
    this.dom ? this.dirty & 4 && this.setAttrs(this.dom) : this.setDOM(this.setAttrs(document.createElement(this.mark.tagName))), super.sync(t3);
  }
  merge(t3, e, i2, n11, r2, o3) {
    return i2 && (!(i2 instanceof s23 && i2.mark.eq(this.mark)) || t3 && r2 <= 0 || e < this.length && o3 <= 0) ? false : (gs(this, t3, e, i2 ? i2.children : [], r2 - 1, o3 - 1), this.markDirty(), true);
  }
  split(t3) {
    let e = [], i2 = 0, n11 = -1, r2 = 0;
    for (let l9 of this.children) {
      let h = i2 + l9.length;
      h > t3 && e.push(i2 < t3 ? l9.split(t3 - i2) : l9), n11 < 0 && i2 >= t3 && (n11 = r2), i2 = h, r2++;
    }
    let o3 = this.length - t3;
    return this.length = t3, n11 > -1 && (this.children.length = n11, this.markDirty()), new s23(this.mark, e, o3);
  }
  domAtPos(t3) {
    return vs(this.dom, this.children, t3);
  }
  coordsAt(t3, e) {
    return Ss(this, t3, e);
  }
};
function Be2(s45, t3, e) {
  let i2 = s45.nodeValue.length;
  t3 > i2 && (t3 = i2);
  let n11 = t3, r2 = t3, o3 = 0;
  t3 == 0 && e < 0 || t3 == i2 && e >= 0 ? g2.chrome || g2.gecko || (t3 ? (n11--, o3 = 1) : r2 < i2 && (r2++, o3 = -1)) : e < 0 ? n11-- : r2 < i2 && r2++;
  let l9 = Ot(s45, n11, r2).getClientRects();
  if (!l9.length) return ds;
  let h = l9[(o3 ? o3 < 0 : e >= 0) ? 0 : l9.length - 1];
  return g2.safari && !o3 && h.width == 0 && (h = Array.prototype.find.call(l9, (a2) => a2.width) || h), o3 ? ge2(h, o3 < 0) : h || null;
}
var Rt = class s24 extends R2 {
  constructor(t3, e, i2) {
    super(), this.widget = t3, this.length = e, this.side = i2, this.prevWidget = null;
  }
  static create(t3, e, i2) {
    return new (t3.customView || s24)(t3, e, i2);
  }
  split(t3) {
    let e = s24.create(this.widget, this.length - t3, this.side);
    return this.length -= t3, e;
  }
  sync() {
    (!this.dom || !this.widget.updateDOM(this.dom)) && (this.dom && this.prevWidget && this.prevWidget.destroy(this.dom), this.prevWidget = null, this.setDOM(this.widget.toDOM(this.editorView)), this.dom.contentEditable = "false");
  }
  getSide() {
    return this.side;
  }
  merge(t3, e, i2, n11, r2, o3) {
    return i2 && (!(i2 instanceof s24) || !this.widget.compare(i2.widget) || t3 > 0 && r2 <= 0 || e < this.length && o3 <= 0) ? false : (this.length = t3 + (i2 ? i2.length : 0) + (this.length - e), true);
  }
  become(t3) {
    return t3.length == this.length && t3 instanceof s24 && t3.side == this.side && this.widget.constructor == t3.widget.constructor ? (this.widget.eq(t3.widget) || this.markDirty(true), this.dom && !this.prevWidget && (this.prevWidget = this.widget), this.widget = t3.widget, true) : false;
  }
  ignoreMutation() {
    return true;
  }
  ignoreEvent(t3) {
    return this.widget.ignoreEvent(t3);
  }
  get overrideDOMText() {
    if (this.length == 0) return m.empty;
    let t3 = this;
    for (; t3.parent; ) t3 = t3.parent;
    let e = t3.editorView, i2 = e && e.state.doc, n11 = this.posAtStart;
    return i2 ? i2.slice(n11, n11 + this.length) : m.empty;
  }
  domAtPos(t3) {
    return t3 == 0 ? B2.before(this.dom) : B2.after(this.dom, t3 == this.length);
  }
  domBoundsAround() {
    return null;
  }
  coordsAt(t3, e) {
    let i2 = this.dom.getClientRects(), n11 = null;
    if (!i2.length) return ds;
    for (let r2 = t3 > 0 ? i2.length - 1 : 0; n11 = i2[r2], !(t3 > 0 ? r2 == 0 : r2 == i2.length - 1 || n11.top < n11.bottom); r2 += t3 > 0 ? -1 : 1) ;
    return t3 == 0 && e > 0 || t3 == this.length && e <= 0 ? n11 : ge2(n11, t3 == 0);
  }
  get isEditable() {
    return false;
  }
  destroy() {
    super.destroy(), this.dom && this.widget.destroy(this.dom);
  }
};
var Zt = class extends Rt {
  domAtPos(t3) {
    let { topView: e, text: i2 } = this.widget;
    return e ? He2(t3, 0, e, i2, (n11, r2) => n11.domAtPos(r2), (n11) => new B2(i2, Math.min(n11, i2.nodeValue.length))) : new B2(i2, Math.min(t3, i2.nodeValue.length));
  }
  sync() {
    this.setDOM(this.widget.toDOM());
  }
  localPosFromDOM(t3, e) {
    let { topView: i2, text: n11 } = this.widget;
    return i2 ? ws(t3, e, i2, n11) : Math.min(e, this.length);
  }
  ignoreMutation() {
    return false;
  }
  get overrideDOMText() {
    return null;
  }
  coordsAt(t3, e) {
    let { topView: i2, text: n11 } = this.widget;
    return i2 ? He2(t3, e, i2, n11, (r2, o3, l9) => r2.coordsAt(o3, l9), (r2, o3) => Be2(n11, r2, o3)) : Be2(n11, t3, e);
  }
  destroy() {
    var t3;
    super.destroy(), (t3 = this.widget.topView) === null || t3 === void 0 || t3.destroy();
  }
  get isEditable() {
    return true;
  }
};
function He2(s45, t3, e, i2, n11, r2) {
  if (e instanceof q2) {
    for (let o3 of e.children) {
      let l9 = pt(o3.dom, i2), h = l9 ? i2.nodeValue.length : o3.length;
      if (s45 < h || s45 == h && o3.getSide() <= 0) return l9 ? He2(s45, t3, o3, i2, n11, r2) : n11(o3, s45, t3);
      s45 -= h;
    }
    return n11(e, e.length, -1);
  } else return e.dom == i2 ? r2(s45, t3) : n11(e, s45, t3);
}
function ws(s45, t3, e, i2) {
  if (e instanceof q2) for (let n11 of e.children) {
    let r2 = 0, o3 = pt(n11.dom, i2);
    if (pt(n11.dom, s45)) return r2 + (o3 ? ws(s45, t3, n11, i2) : n11.localPosFromDOM(s45, t3));
    r2 += o3 ? i2.nodeValue.length : n11.length;
  }
  else if (e.dom == i2) return Math.min(t3, i2.nodeValue.length);
  return e.localPosFromDOM(s45, t3);
}
var Lt = class s25 extends R2 {
  constructor(t3) {
    super(), this.side = t3;
  }
  get length() {
    return 0;
  }
  merge() {
    return false;
  }
  become(t3) {
    return t3 instanceof s25 && t3.side == this.side;
  }
  split() {
    return new s25(this.side);
  }
  sync() {
    if (!this.dom) {
      let t3 = document.createElement("img");
      t3.className = "cm-widgetBuffer", t3.setAttribute("aria-hidden", "true"), this.setDOM(t3);
    }
  }
  getSide() {
    return this.side;
  }
  domAtPos(t3) {
    return B2.before(this.dom);
  }
  localPosFromDOM() {
    return 0;
  }
  domBoundsAround() {
    return null;
  }
  coordsAt(t3) {
    let e = this.dom.getBoundingClientRect(), i2 = xn(this, this.side > 0 ? -1 : 1);
    return i2 && i2.top < e.bottom && i2.bottom > e.top ? {
      left: e.left,
      right: e.right,
      top: i2.top,
      bottom: i2.bottom
    } : e;
  }
  get overrideDOMText() {
    return m.empty;
  }
};
rt2.prototype.children = Rt.prototype.children = Lt.prototype.children = mi;
function xn(s45, t3) {
  let e = s45.parent, i2 = e ? e.children.indexOf(s45) : -1;
  for (; e && i2 >= 0; ) if (t3 < 0 ? i2 > 0 : i2 < e.children.length) {
    let n11 = e.children[i2 + t3];
    if (n11 instanceof rt2) {
      let r2 = n11.coordsAt(t3 < 0 ? n11.length : 0, t3);
      if (r2) return r2;
    }
    i2 += t3;
  } else if (e instanceof q2 && e.parent) i2 = e.parent.children.indexOf(e) + (t3 < 0 ? 0 : 1), e = e.parent;
  else {
    let n11 = e.dom.lastChild;
    if (n11 && n11.nodeName == "BR") return n11.getClientRects()[0];
    break;
  }
}
function vs(s45, t3, e) {
  let i2 = 0;
  for (let n11 = 0; i2 < t3.length; i2++) {
    let r2 = t3[i2], o3 = n11 + r2.length;
    if (!(o3 == n11 && r2.getSide() <= 0)) {
      if (e > n11 && e < o3 && r2.dom.parentNode == s45) return r2.domAtPos(e - n11);
      if (e <= n11) break;
      n11 = o3;
    }
  }
  for (; i2 > 0; i2--) {
    let n11 = t3[i2 - 1].dom;
    if (n11.parentNode == s45) return B2.after(n11);
  }
  return new B2(s45, 0);
}
function xs(s45, t3, e) {
  let i2, { children: n11 } = s45;
  e > 0 && t3 instanceof q2 && n11.length && (i2 = n11[n11.length - 1]) instanceof q2 && i2.mark.eq(t3.mark) ? xs(i2, t3.children[0], e - 1) : (n11.push(t3), t3.setParent(s45)), s45.length += t3.length;
}
function Ss(s45, t3, e) {
  for (let r2 = 0, o3 = 0; o3 < s45.children.length; o3++) {
    let l9 = s45.children[o3], h = r2 + l9.length, a2;
    if ((e <= 0 || h == s45.length || l9.getSide() > 0 ? h >= t3 : h > t3) && (t3 < h || o3 + 1 == s45.children.length || (a2 = s45.children[o3 + 1]).length || a2.getSide() > 0)) {
      let c3 = 0;
      if (h == r2) {
        if (l9.getSide() <= 0) continue;
        c3 = e = -l9.getSide();
      }
      let f = l9.coordsAt(Math.max(0, t3 - r2), e);
      return c3 && f ? ge2(f, e < 0) : f;
    }
    r2 = h;
  }
  let i2 = s45.dom.lastChild;
  if (!i2) return s45.dom.getBoundingClientRect();
  let n11 = Tt(i2);
  return n11[n11.length - 1] || null;
}
function Pe2(s45, t3) {
  for (let e in s45) e == "class" && t3.class ? t3.class += " " + s45.class : e == "style" && t3.style ? t3.style += ";" + s45.style : t3[e] = s45[e];
  return t3;
}
function gi(s45, t3) {
  if (s45 == t3) return true;
  if (!s45 || !t3) return false;
  let e = Object.keys(s45), i2 = Object.keys(t3);
  if (e.length != i2.length) return false;
  for (let n11 of e) if (i2.indexOf(n11) == -1 || s45[n11] !== t3[n11]) return false;
  return true;
}
function Ve2(s45, t3, e) {
  let i2 = null;
  if (t3) for (let n11 in t3) e && n11 in e || s45.removeAttribute(i2 = n11);
  if (e) for (let n11 in e) t3 && t3[n11] == e[n11] || s45.setAttribute(i2 = n11, e[n11]);
  return !!i2;
}
var K2 = class {
  eq(t3) {
    return false;
  }
  updateDOM(t3) {
    return false;
  }
  compare(t3) {
    return this == t3 || this.constructor == t3.constructor && this.eq(t3);
  }
  get estimatedHeight() {
    return -1;
  }
  ignoreEvent(t3) {
    return true;
  }
  get customView() {
    return null;
  }
  destroy(t3) {
  }
};
var D2 = function(s45) {
  return s45[s45.Text = 0] = "Text", s45[s45.WidgetBefore = 1] = "WidgetBefore", s45[s45.WidgetAfter = 2] = "WidgetAfter", s45[s45.WidgetRange = 3] = "WidgetRange", s45;
}(D2 || (D2 = {}));
var C2 = class extends z {
  constructor(t3, e, i2, n11) {
    super(), this.startSide = t3, this.endSide = e, this.widget = i2, this.spec = n11;
  }
  get heightRelevant() {
    return false;
  }
  static mark(t3) {
    return new Qt(t3);
  }
  static widget(t3) {
    let e = t3.side || 0, i2 = !!t3.block;
    return e += i2 ? e > 0 ? 3e8 : -4e8 : e > 0 ? 1e8 : -1e8, new ot2(t3, e, e, i2, t3.widget || null, false);
  }
  static replace(t3) {
    let e = !!t3.block, i2, n11;
    if (t3.isBlockGap) i2 = -5e8, n11 = 4e8;
    else {
      let { start: r2, end: o3 } = Cs(t3, e);
      i2 = (r2 ? e ? -3e8 : -1 : 5e8) - 1, n11 = (o3 ? e ? 2e8 : 1 : -6e8) + 1;
    }
    return new ot2(t3, i2, n11, e, t3.widget || null, true);
  }
  static line(t3) {
    return new Et(t3);
  }
  static set(t3, e = false) {
    return O.of(t3, e);
  }
  hasHeight() {
    return this.widget ? this.widget.estimatedHeight > -1 : false;
  }
};
C2.none = O.empty;
var Qt = class s26 extends C2 {
  constructor(t3) {
    let { start: e, end: i2 } = Cs(t3);
    super(e ? -1 : 5e8, i2 ? 1 : -6e8, null, t3), this.tagName = t3.tagName || "span", this.class = t3.class || "", this.attrs = t3.attributes || null;
  }
  eq(t3) {
    return this == t3 || t3 instanceof s26 && this.tagName == t3.tagName && this.class == t3.class && gi(this.attrs, t3.attrs);
  }
  range(t3, e = t3) {
    if (t3 >= e) throw new RangeError("Mark decorations may not be empty");
    return super.range(t3, e);
  }
};
Qt.prototype.point = false;
var Et = class s27 extends C2 {
  constructor(t3) {
    super(-2e8, -2e8, null, t3);
  }
  eq(t3) {
    return t3 instanceof s27 && gi(this.spec.attributes, t3.spec.attributes);
  }
  range(t3, e = t3) {
    if (e != t3) throw new RangeError("Line decoration ranges must be zero-length");
    return super.range(t3, e);
  }
};
Et.prototype.mapMode = b.TrackBefore;
Et.prototype.point = true;
var ot2 = class s28 extends C2 {
  constructor(t3, e, i2, n11, r2, o3) {
    super(e, i2, r2, t3), this.block = n11, this.isReplace = o3, this.mapMode = n11 ? e <= 0 ? b.TrackBefore : b.TrackAfter : b.TrackDel;
  }
  get type() {
    return this.startSide < this.endSide ? D2.WidgetRange : this.startSide <= 0 ? D2.WidgetBefore : D2.WidgetAfter;
  }
  get heightRelevant() {
    return this.block || !!this.widget && this.widget.estimatedHeight >= 5;
  }
  eq(t3) {
    return t3 instanceof s28 && Sn(this.widget, t3.widget) && this.block == t3.block && this.startSide == t3.startSide && this.endSide == t3.endSide;
  }
  range(t3, e = t3) {
    if (this.isReplace && (t3 > e || t3 == e && this.startSide > 0 && this.endSide <= 0)) throw new RangeError("Invalid range for replacement decoration");
    if (!this.isReplace && e != t3) throw new RangeError("Widget decorations can only have zero-length ranges");
    return super.range(t3, e);
  }
};
ot2.prototype.point = true;
function Cs(s45, t3 = false) {
  let { inclusiveStart: e, inclusiveEnd: i2 } = s45;
  return e == null && (e = s45.inclusive), i2 == null && (i2 = s45.inclusive), {
    start: e ?? t3,
    end: i2 ?? t3
  };
}
function Sn(s45, t3) {
  return s45 == t3 || !!(s45 && t3 && s45.compare(t3));
}
function Ne2(s45, t3, e, i2 = 0) {
  let n11 = e.length - 1;
  n11 >= 0 && e[n11] + i2 >= s45 ? e[n11] = Math.max(e[n11], t3) : e.push(s45, t3);
}
var N2 = class s29 extends R2 {
  constructor() {
    super(...arguments), this.children = [], this.length = 0, this.prevAttrs = void 0, this.attrs = null, this.breakAfter = 0;
  }
  merge(t3, e, i2, n11, r2, o3) {
    if (i2) {
      if (!(i2 instanceof s29)) return false;
      this.dom || i2.transferDOM(this);
    }
    return n11 && this.setDeco(i2 ? i2.attrs : null), gs(this, t3, e, i2 ? i2.children : [], r2, o3), true;
  }
  split(t3) {
    let e = new s29();
    if (e.breakAfter = this.breakAfter, this.length == 0) return e;
    let { i: i2, off: n11 } = this.childPos(t3);
    n11 && (e.append(this.children[i2].split(n11), 0), this.children[i2].merge(n11, this.children[i2].length, null, false, 0, 0), i2++);
    for (let r2 = i2; r2 < this.children.length; r2++) e.append(this.children[r2], 0);
    for (; i2 > 0 && this.children[i2 - 1].length == 0; ) this.children[--i2].destroy();
    return this.children.length = i2, this.markDirty(), this.length = t3, e;
  }
  transferDOM(t3) {
    this.dom && (this.markDirty(), t3.setDOM(this.dom), t3.prevAttrs = this.prevAttrs === void 0 ? this.attrs : this.prevAttrs, this.prevAttrs = void 0, this.dom = null);
  }
  setDeco(t3) {
    gi(this.attrs, t3) || (this.dom && (this.prevAttrs = this.attrs, this.markDirty()), this.attrs = t3);
  }
  append(t3, e) {
    xs(this, t3, e);
  }
  addLineDeco(t3) {
    let e = t3.spec.attributes, i2 = t3.spec.class;
    e && (this.attrs = Pe2(e, this.attrs || {})), i2 && (this.attrs = Pe2({
      class: i2
    }, this.attrs || {}));
  }
  domAtPos(t3) {
    return vs(this.dom, this.children, t3);
  }
  reuseDOM(t3) {
    t3.nodeName == "DIV" && (this.setDOM(t3), this.dirty |= 6);
  }
  sync(t3) {
    var e;
    this.dom ? this.dirty & 4 && (ps(this.dom), this.dom.className = "cm-line", this.prevAttrs = this.attrs ? null : void 0) : (this.setDOM(document.createElement("div")), this.dom.className = "cm-line", this.prevAttrs = this.attrs ? null : void 0), this.prevAttrs !== void 0 && (Ve2(this.dom, this.prevAttrs, this.attrs), this.dom.classList.add("cm-line"), this.prevAttrs = void 0), super.sync(t3);
    let i2 = this.dom.lastChild;
    for (; i2 && R2.get(i2) instanceof q2; ) i2 = i2.lastChild;
    if (!i2 || !this.length || i2.nodeName != "BR" && ((e = R2.get(i2)) === null || e === void 0 ? void 0 : e.isEditable) == false && (!g2.ios || !this.children.some((n11) => n11 instanceof rt2))) {
      let n11 = document.createElement("BR");
      n11.cmIgnore = true, this.dom.appendChild(n11);
    }
  }
  measureTextSize() {
    if (this.children.length == 0 || this.length > 20) return null;
    let t3 = 0;
    for (let e of this.children) {
      if (!(e instanceof rt2)) return null;
      let i2 = Tt(e.dom);
      if (i2.length != 1) return null;
      t3 += i2[0].width;
    }
    return {
      lineHeight: this.dom.getBoundingClientRect().height,
      charWidth: t3 / this.length
    };
  }
  coordsAt(t3, e) {
    return Ss(this, t3, e);
  }
  become(t3) {
    return false;
  }
  get type() {
    return D2.Text;
  }
  static find(t3, e) {
    for (let i2 = 0, n11 = 0; i2 < t3.children.length; i2++) {
      let r2 = t3.children[i2], o3 = n11 + r2.length;
      if (o3 >= e) {
        if (r2 instanceof s29) return r2;
        if (o3 > e) break;
      }
      n11 = o3 + r2.breakAfter;
    }
    return null;
  }
};
var Bt = class s30 extends R2 {
  constructor(t3, e, i2) {
    super(), this.widget = t3, this.length = e, this.type = i2, this.breakAfter = 0, this.prevWidget = null;
  }
  merge(t3, e, i2, n11, r2, o3) {
    return i2 && (!(i2 instanceof s30) || !this.widget.compare(i2.widget) || t3 > 0 && r2 <= 0 || e < this.length && o3 <= 0) ? false : (this.length = t3 + (i2 ? i2.length : 0) + (this.length - e), true);
  }
  domAtPos(t3) {
    return t3 == 0 ? B2.before(this.dom) : B2.after(this.dom, t3 == this.length);
  }
  split(t3) {
    let e = this.length - t3;
    this.length = t3;
    let i2 = new s30(this.widget, e, this.type);
    return i2.breakAfter = this.breakAfter, i2;
  }
  get children() {
    return mi;
  }
  sync() {
    (!this.dom || !this.widget.updateDOM(this.dom)) && (this.dom && this.prevWidget && this.prevWidget.destroy(this.dom), this.prevWidget = null, this.setDOM(this.widget.toDOM(this.editorView)), this.dom.contentEditable = "false");
  }
  get overrideDOMText() {
    return this.parent ? this.parent.view.state.doc.slice(this.posAtStart, this.posAtEnd) : m.empty;
  }
  domBoundsAround() {
    return null;
  }
  become(t3) {
    return t3 instanceof s30 && t3.type == this.type && t3.widget.constructor == this.widget.constructor ? (t3.widget.eq(this.widget) || this.markDirty(true), this.dom && !this.prevWidget && (this.prevWidget = this.widget), this.widget = t3.widget, this.length = t3.length, this.breakAfter = t3.breakAfter, true) : false;
  }
  ignoreMutation() {
    return true;
  }
  ignoreEvent(t3) {
    return this.widget.ignoreEvent(t3);
  }
  destroy() {
    super.destroy(), this.dom && this.widget.destroy(this.dom);
  }
};
var We2 = class s31 {
  constructor(t3, e, i2, n11) {
    this.doc = t3, this.pos = e, this.end = i2, this.disallowBlockEffectsFor = n11, this.content = [], this.curLine = null, this.breakAtStart = 0, this.pendingBuffer = 0, this.atCursorPos = true, this.openStart = -1, this.openEnd = -1, this.text = "", this.textOff = 0, this.cursor = t3.iter(), this.skip = e;
  }
  posCovered() {
    if (this.content.length == 0) return !this.breakAtStart && this.doc.lineAt(this.pos).from != this.pos;
    let t3 = this.content[this.content.length - 1];
    return !t3.breakAfter && !(t3 instanceof Bt && t3.type == D2.WidgetBefore);
  }
  getLine() {
    return this.curLine || (this.content.push(this.curLine = new N2()), this.atCursorPos = true), this.curLine;
  }
  flushBuffer(t3) {
    this.pendingBuffer && (this.curLine.append(It(new Lt(-1), t3), t3.length), this.pendingBuffer = 0);
  }
  addBlockWidget(t3) {
    this.flushBuffer([]), this.curLine = null, this.content.push(t3);
  }
  finish(t3) {
    t3 ? this.pendingBuffer = 0 : this.flushBuffer([]), this.posCovered() || this.getLine();
  }
  buildText(t3, e, i2) {
    for (; t3 > 0; ) {
      if (this.textOff == this.text.length) {
        let { value: r2, lineBreak: o3, done: l9 } = this.cursor.next(this.skip);
        if (this.skip = 0, l9) throw new Error("Ran out of text content when drawing inline views");
        if (o3) {
          this.posCovered() || this.getLine(), this.content.length ? this.content[this.content.length - 1].breakAfter = 1 : this.breakAtStart = 1, this.flushBuffer([]), this.curLine = null, t3--;
          continue;
        } else this.text = r2, this.textOff = 0;
      }
      let n11 = Math.min(this.text.length - this.textOff, t3, 512);
      this.flushBuffer(e.slice(0, i2)), this.getLine().append(It(new rt2(this.text.slice(this.textOff, this.textOff + n11)), e), i2), this.atCursorPos = true, this.textOff += n11, t3 -= n11, i2 = 0;
    }
  }
  span(t3, e, i2, n11) {
    this.buildText(e - t3, i2, n11), this.pos = e, this.openStart < 0 && (this.openStart = n11);
  }
  point(t3, e, i2, n11, r2, o3) {
    if (this.disallowBlockEffectsFor[o3] && i2 instanceof ot2) {
      if (i2.block) throw new RangeError("Block decorations may not be specified via plugins");
      if (e > this.doc.lineAt(this.pos).to) throw new RangeError("Decorations that replace line breaks may not be specified via plugins");
    }
    let l9 = e - t3;
    if (i2 instanceof ot2) if (i2.block) {
      let { type: h } = i2;
      h == D2.WidgetAfter && !this.posCovered() && this.getLine(), this.addBlockWidget(new Bt(i2.widget || new te2("div"), l9, h));
    } else {
      let h = Rt.create(i2.widget || new te2("span"), l9, i2.startSide), a2 = this.atCursorPos && !h.isEditable && r2 <= n11.length && (t3 < e || i2.startSide > 0), c3 = !h.isEditable && (t3 < e || i2.startSide <= 0), f = this.getLine();
      this.pendingBuffer == 2 && !a2 && (this.pendingBuffer = 0), this.flushBuffer(n11), a2 && (f.append(It(new Lt(1), n11), r2), r2 = n11.length + Math.max(0, r2 - n11.length)), f.append(It(h, n11), r2), this.atCursorPos = c3, this.pendingBuffer = c3 ? t3 < e ? 1 : 2 : 0;
    }
    else this.doc.lineAt(this.pos).from == this.pos && this.getLine().addLineDeco(i2);
    l9 && (this.textOff + l9 <= this.text.length ? this.textOff += l9 : (this.skip += l9 - (this.text.length - this.textOff), this.text = "", this.textOff = 0), this.pos = e), this.openStart < 0 && (this.openStart = r2);
  }
  static build(t3, e, i2, n11, r2) {
    let o3 = new s31(t3, e, i2, r2);
    return o3.openEnd = O.spans(n11, e, i2, o3), o3.openStart < 0 && (o3.openStart = o3.openEnd), o3.finish(o3.openEnd), o3;
  }
};
function It(s45, t3) {
  for (let e of t3) s45 = new q2(e, [
    s45
  ], s45.length);
  return s45;
}
var te2 = class extends K2 {
  constructor(t3) {
    super(), this.tag = t3;
  }
  eq(t3) {
    return t3.tag == this.tag;
  }
  toDOM() {
    return document.createElement(this.tag);
  }
  updateDOM(t3) {
    return t3.nodeName.toLowerCase() == this.tag;
  }
};
var Ms = y.define();
var ks = y.define();
var As = y.define();
var Ds = y.define();
var ze2 = y.define();
var Ts = y.define();
var Os = y.define({
  combine: (s45) => s45.some((t3) => t3)
});
var ee2 = class s32 {
  constructor(t3, e = "nearest", i2 = "nearest", n11 = 5, r2 = 5) {
    this.range = t3, this.y = e, this.x = i2, this.yMargin = n11, this.xMargin = r2;
  }
  map(t3) {
    return t3.empty ? this : new s32(this.range.map(t3), this.y, this.x, this.yMargin, this.xMargin);
  }
};
var Di = v.define({
  map: (s45, t3) => s45.map(t3)
});
function Z2(s45, t3, e) {
  let i2 = s45.facet(Ds);
  i2.length ? i2[0](t3) : globalThis.onerror ? globalThis.onerror(String(t3), e, void 0, void 0, t3) : e ? console.error(e + ":", t3) : console.error(t3);
}
var Nt = y.define({
  combine: (s45) => s45.length ? s45[0] : true
});
var Cn = 0;
var bt = y.define();
var P2 = class s33 {
  constructor(t3, e, i2, n11) {
    this.id = t3, this.create = e, this.domEventHandlers = i2, this.extension = n11(this);
  }
  static define(t3, e) {
    let { eventHandlers: i2, provide: n11, decorations: r2 } = e || {};
    return new s33(Cn++, t3, i2, (o3) => {
      let l9 = [
        bt.of(o3)
      ];
      return r2 && l9.push(Ht.of((h) => {
        let a2 = h.plugin(o3);
        return a2 ? r2(a2) : C2.none;
      })), n11 && l9.push(n11(o3)), l9;
    });
  }
  static fromClass(t3, e) {
    return s33.define((i2) => new t3(i2), e);
  }
};
var Mt = class {
  constructor(t3) {
    this.spec = t3, this.mustUpdate = null, this.value = null;
  }
  update(t3) {
    if (this.value) {
      if (this.mustUpdate) {
        let e = this.mustUpdate;
        if (this.mustUpdate = null, this.value.update) try {
          this.value.update(e);
        } catch (i2) {
          if (Z2(e.state, i2, "CodeMirror plugin crashed"), this.value.destroy) try {
            this.value.destroy();
          } catch {
          }
          this.deactivate();
        }
      }
    } else if (this.spec) try {
      this.value = this.spec.create(t3);
    } catch (e) {
      Z2(t3.state, e, "CodeMirror plugin crashed"), this.deactivate();
    }
    return this;
  }
  destroy(t3) {
    var e;
    if (!((e = this.value) === null || e === void 0) && e.destroy) try {
      this.value.destroy();
    } catch (i2) {
      Z2(t3.state, i2, "CodeMirror plugin crashed");
    }
  }
  deactivate() {
    this.spec = this.value = null;
  }
};
var Rs = y.define();
var bi = y.define();
var Ht = y.define();
var Ls = y.define();
var Es = y.define();
var yt = y.define();
var it2 = class s34 {
  constructor(t3, e, i2, n11) {
    this.fromA = t3, this.toA = e, this.fromB = i2, this.toB = n11;
  }
  join(t3) {
    return new s34(Math.min(this.fromA, t3.fromA), Math.max(this.toA, t3.toA), Math.min(this.fromB, t3.fromB), Math.max(this.toB, t3.toB));
  }
  addToSet(t3) {
    let e = t3.length, i2 = this;
    for (; e > 0; e--) {
      let n11 = t3[e - 1];
      if (!(n11.fromA > i2.toA)) {
        if (n11.toA < i2.fromA) break;
        i2 = i2.join(n11), t3.splice(e - 1, 1);
      }
    }
    return t3.splice(e, 0, i2), t3;
  }
  static extendWithRanges(t3, e) {
    if (e.length == 0) return t3;
    let i2 = [];
    for (let n11 = 0, r2 = 0, o3 = 0, l9 = 0; ; n11++) {
      let h = n11 == t3.length ? null : t3[n11], a2 = o3 - l9, c3 = h ? h.fromB : 1e9;
      for (; r2 < e.length && e[r2] < c3; ) {
        let f = e[r2], u2 = e[r2 + 1], d = Math.max(l9, f), p2 = Math.min(c3, u2);
        if (d <= p2 && new s34(d + a2, p2 + a2, d, p2).addToSet(i2), u2 > c3) break;
        r2 += 2;
      }
      if (!h) return i2;
      new s34(h.fromA, h.toA, h.fromB, h.toB).addToSet(i2), o3 = h.toA, l9 = h.toB;
    }
  }
};
var ie2 = class s35 {
  constructor(t3, e, i2) {
    this.view = t3, this.state = e, this.transactions = i2, this.flags = 0, this.startState = t3.state, this.changes = P.empty(this.startState.doc.length);
    for (let o3 of i2) this.changes = this.changes.compose(o3.changes);
    let n11 = [];
    this.changes.iterChangedRanges((o3, l9, h, a2) => n11.push(new it2(o3, l9, h, a2))), this.changedRanges = n11;
    let r2 = t3.hasFocus;
    r2 != t3.inputState.notifiedFocused && (t3.inputState.notifiedFocused = r2, this.flags |= 1);
  }
  static create(t3, e, i2) {
    return new s35(t3, e, i2);
  }
  get viewportChanged() {
    return (this.flags & 4) > 0;
  }
  get heightChanged() {
    return (this.flags & 2) > 0;
  }
  get geometryChanged() {
    return this.docChanged || (this.flags & 10) > 0;
  }
  get focusChanged() {
    return (this.flags & 1) > 0;
  }
  get docChanged() {
    return !this.changes.empty;
  }
  get selectionSet() {
    return this.transactions.some((t3) => t3.selection);
  }
  get empty() {
    return this.flags == 0 && this.transactions.length == 0;
  }
};
var O2 = function(s45) {
  return s45[s45.LTR = 0] = "LTR", s45[s45.RTL = 1] = "RTL", s45;
}(O2 || (O2 = {}));
var Fe2 = O2.LTR;
var Mn = O2.RTL;
function Bs(s45) {
  let t3 = [];
  for (let e = 0; e < s45.length; e++) t3.push(1 << +s45[e]);
  return t3;
}
var kn = Bs("88888888888888888888888888888888888666888888787833333333337888888000000000000000000000000008888880000000000000000000000000088888888888888888888888888888888888887866668888088888663380888308888800000000000000000000000800000000000000000000000000000008");
var An = Bs("4444448826627288999999999992222222222222222222222222222222222222222222222229999999999999999999994444444444644222822222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222999999949999999229989999223333333333");
var Ie2 = /* @__PURE__ */ Object.create(null);
var F2 = [];
for (let s45 of [
  "()",
  "[]",
  "{}"
]) {
  let t3 = s45.charCodeAt(0), e = s45.charCodeAt(1);
  Ie2[t3] = e, Ie2[e] = -t3;
}
function Dn(s45) {
  return s45 <= 247 ? kn[s45] : 1424 <= s45 && s45 <= 1524 ? 2 : 1536 <= s45 && s45 <= 1785 ? An[s45 - 1536] : 1774 <= s45 && s45 <= 2220 ? 4 : 8192 <= s45 && s45 <= 8203 || s45 == 8204 ? 256 : 1;
}
var Tn = /[\u0590-\u05f4\u0600-\u06ff\u0700-\u08ac]/;
var Q2 = class {
  constructor(t3, e, i2) {
    this.from = t3, this.to = e, this.level = i2;
  }
  get dir() {
    return this.level % 2 ? Mn : Fe2;
  }
  side(t3, e) {
    return this.dir == e == t3 ? this.to : this.from;
  }
  static find(t3, e, i2, n11) {
    let r2 = -1;
    for (let o3 = 0; o3 < t3.length; o3++) {
      let l9 = t3[o3];
      if (l9.from <= e && l9.to >= e) {
        if (l9.level == i2) return o3;
        (r2 < 0 || (n11 != 0 ? n11 < 0 ? l9.from < e : l9.to > e : t3[r2].level > l9.level)) && (r2 = o3);
      }
    }
    if (r2 < 0) throw new RangeError("Index out of range");
    return r2;
  }
};
var T3 = [];
function Hs(s45, t3) {
  let e = s45.length, i2 = t3 == Fe2 ? 1 : 2, n11 = t3 == Fe2 ? 2 : 1;
  if (!s45 || i2 == 1 && !Tn.test(s45)) return Ps(e);
  for (let o3 = 0, l9 = i2, h = i2; o3 < e; o3++) {
    let a2 = Dn(s45.charCodeAt(o3));
    a2 == 512 ? a2 = l9 : a2 == 8 && h == 4 && (a2 = 16), T3[o3] = a2 == 4 ? 2 : a2, a2 & 7 && (h = a2), l9 = a2;
  }
  for (let o3 = 0, l9 = i2, h = i2; o3 < e; o3++) {
    let a2 = T3[o3];
    if (a2 == 128) o3 < e - 1 && l9 == T3[o3 + 1] && l9 & 24 ? a2 = T3[o3] = l9 : T3[o3] = 256;
    else if (a2 == 64) {
      let c3 = o3 + 1;
      for (; c3 < e && T3[c3] == 64; ) c3++;
      let f = o3 && l9 == 8 || c3 < e && T3[c3] == 8 ? h == 1 ? 1 : 8 : 256;
      for (let u2 = o3; u2 < c3; u2++) T3[u2] = f;
      o3 = c3 - 1;
    } else a2 == 8 && h == 1 && (T3[o3] = 1);
    l9 = a2, a2 & 7 && (h = a2);
  }
  for (let o3 = 0, l9 = 0, h = 0, a2, c3, f; o3 < e; o3++) if (c3 = Ie2[a2 = s45.charCodeAt(o3)]) if (c3 < 0) {
    for (let u2 = l9 - 3; u2 >= 0; u2 -= 3) if (F2[u2 + 1] == -c3) {
      let d = F2[u2 + 2], p2 = d & 2 ? i2 : d & 4 ? d & 1 ? n11 : i2 : 0;
      p2 && (T3[o3] = T3[F2[u2]] = p2), l9 = u2;
      break;
    }
  } else {
    if (F2.length == 189) break;
    F2[l9++] = o3, F2[l9++] = a2, F2[l9++] = h;
  }
  else if ((f = T3[o3]) == 2 || f == 1) {
    let u2 = f == i2;
    h = u2 ? 0 : 1;
    for (let d = l9 - 3; d >= 0; d -= 3) {
      let p2 = F2[d + 2];
      if (p2 & 2) break;
      if (u2) F2[d + 2] |= 2;
      else {
        if (p2 & 4) break;
        F2[d + 2] |= 4;
      }
    }
  }
  for (let o3 = 0; o3 < e; o3++) if (T3[o3] == 256) {
    let l9 = o3 + 1;
    for (; l9 < e && T3[l9] == 256; ) l9++;
    let h = (o3 ? T3[o3 - 1] : i2) == 1, a2 = (l9 < e ? T3[l9] : i2) == 1, c3 = h == a2 ? h ? 1 : 2 : i2;
    for (let f = o3; f < l9; f++) T3[f] = c3;
    o3 = l9 - 1;
  }
  let r2 = [];
  if (i2 == 1) for (let o3 = 0; o3 < e; ) {
    let l9 = o3, h = T3[o3++] != 1;
    for (; o3 < e && h == (T3[o3] != 1); ) o3++;
    if (h) for (let a2 = o3; a2 > l9; ) {
      let c3 = a2, f = T3[--a2] != 2;
      for (; a2 > l9 && f == (T3[a2 - 1] != 2); ) a2--;
      r2.push(new Q2(a2, c3, f ? 2 : 1));
    }
    else r2.push(new Q2(l9, o3, 0));
  }
  else for (let o3 = 0; o3 < e; ) {
    let l9 = o3, h = T3[o3++] == 2;
    for (; o3 < e && h == (T3[o3] == 2); ) o3++;
    r2.push(new Q2(l9, o3, h ? 1 : 2));
  }
  return r2;
}
function Ps(s45) {
  return [
    new Q2(0, s45, 0)
  ];
}
var Vs = "";
function Ns(s45, t3, e, i2, n11) {
  var r2;
  let o3 = i2.head - s45.from, l9 = -1;
  if (o3 == 0) {
    if (!n11 || !s45.length) return null;
    t3[0].level != e && (o3 = t3[0].side(false, e), l9 = 0);
  } else if (o3 == s45.length) {
    if (n11) return null;
    let u2 = t3[t3.length - 1];
    u2.level != e && (o3 = u2.side(true, e), l9 = t3.length - 1);
  }
  l9 < 0 && (l9 = Q2.find(t3, o3, (r2 = i2.bidiLevel) !== null && r2 !== void 0 ? r2 : -1, i2.assoc));
  let h = t3[l9];
  o3 == h.side(n11, e) && (h = t3[l9 += n11 ? 1 : -1], o3 = h.side(!n11, e));
  let a2 = n11 == (h.dir == e), c3 = _(s45.text, o3, a2);
  if (Vs = s45.text.slice(Math.min(o3, c3), Math.max(o3, c3)), c3 != h.side(n11, e)) return x.cursor(c3 + s45.from, a2 ? -1 : 1, h.level);
  let f = l9 == (n11 ? t3.length - 1 : 0) ? null : t3[l9 + (n11 ? 1 : -1)];
  return !f && h.level != e ? x.cursor(n11 ? s45.to : s45.from, n11 ? -1 : 1, e) : f && f.level < h.level ? x.cursor(f.side(!n11, e) + s45.from, n11 ? 1 : -1, f.level) : x.cursor(c3 + s45.from, n11 ? -1 : 1, h.level);
}
var X2 = "\uFFFF";
var se2 = class {
  constructor(t3, e) {
    this.points = t3, this.text = "", this.lineSeparator = e.facet(I.lineSeparator);
  }
  append(t3) {
    this.text += t3;
  }
  lineBreak() {
    this.text += X2;
  }
  readRange(t3, e) {
    if (!t3) return this;
    let i2 = t3.parentNode;
    for (let n11 = t3; ; ) {
      this.findPointBefore(i2, n11), this.readNode(n11);
      let r2 = n11.nextSibling;
      if (r2 == e) break;
      let o3 = R2.get(n11), l9 = R2.get(r2);
      (o3 && l9 ? o3.breakAfter : (o3 ? o3.breakAfter : Ti(n11)) || Ti(r2) && (n11.nodeName != "BR" || n11.cmIgnore)) && this.lineBreak(), n11 = r2;
    }
    return this.findPointBefore(i2, e), this;
  }
  readTextNode(t3) {
    let e = t3.nodeValue;
    for (let i2 of this.points) i2.node == t3 && (i2.pos = this.text.length + Math.min(i2.offset, e.length));
    for (let i2 = 0, n11 = this.lineSeparator ? null : /\r\n?|\n/g; ; ) {
      let r2 = -1, o3 = 1, l9;
      if (this.lineSeparator ? (r2 = e.indexOf(this.lineSeparator, i2), o3 = this.lineSeparator.length) : (l9 = n11.exec(e)) && (r2 = l9.index, o3 = l9[0].length), this.append(e.slice(i2, r2 < 0 ? e.length : r2)), r2 < 0) break;
      if (this.lineBreak(), o3 > 1) for (let h of this.points) h.node == t3 && h.pos > this.text.length && (h.pos -= o3 - 1);
      i2 = r2 + o3;
    }
  }
  readNode(t3) {
    if (t3.cmIgnore) return;
    let e = R2.get(t3), i2 = e && e.overrideDOMText;
    if (i2 != null) {
      this.findPointInside(t3, i2.length);
      for (let n11 = i2.iter(); !n11.next().done; ) n11.lineBreak ? this.lineBreak() : this.append(n11.value);
    } else t3.nodeType == 3 ? this.readTextNode(t3) : t3.nodeName == "BR" ? t3.nextSibling && this.lineBreak() : t3.nodeType == 1 && this.readRange(t3.firstChild, null);
  }
  findPointBefore(t3, e) {
    for (let i2 of this.points) i2.node == t3 && t3.childNodes[i2.offset] == e && (i2.pos = this.text.length);
  }
  findPointInside(t3, e) {
    for (let i2 of this.points) (t3.nodeType == 3 ? i2.node == t3 : t3.contains(i2.node)) && (i2.pos = this.text.length + Math.min(e, i2.offset));
  }
};
function Ti(s45) {
  return s45.nodeType == 1 && /^(DIV|P|LI|UL|OL|BLOCKQUOTE|DD|DT|H\d|SECTION|PRE)$/.test(s45.nodeName);
}
var ne2 = class {
  constructor(t3, e) {
    this.node = t3, this.offset = e, this.pos = -1;
  }
};
var re2 = class extends R2 {
  constructor(t3) {
    super(), this.view = t3, this.compositionDeco = C2.none, this.decorations = [], this.dynamicDecorationMap = [], this.minWidth = 0, this.minWidthFrom = 0, this.minWidthTo = 0, this.impreciseAnchor = null, this.impreciseHead = null, this.forceSelection = false, this.lastUpdate = Date.now(), this.setDOM(t3.contentDOM), this.children = [
      new N2()
    ], this.children[0].setParent(this), this.updateDeco(), this.updateInner([
      new it2(0, 0, 0, t3.state.doc.length)
    ], 0);
  }
  get root() {
    return this.view.root;
  }
  get editorView() {
    return this.view;
  }
  get length() {
    return this.view.state.doc.length;
  }
  update(t3) {
    let e = t3.changedRanges;
    this.minWidth > 0 && e.length && (e.every(({ fromA: o3, toA: l9 }) => l9 < this.minWidthFrom || o3 > this.minWidthTo) ? (this.minWidthFrom = t3.changes.mapPos(this.minWidthFrom, 1), this.minWidthTo = t3.changes.mapPos(this.minWidthTo, 1)) : this.minWidth = this.minWidthFrom = this.minWidthTo = 0), this.view.inputState.composing < 0 ? this.compositionDeco = C2.none : (t3.transactions.length || this.dirty) && (this.compositionDeco = Rn(this.view, t3.changes)), (g2.ie || g2.chrome) && !this.compositionDeco.size && t3 && t3.state.doc.lines != t3.startState.doc.lines && (this.forceSelection = true);
    let i2 = this.decorations, n11 = this.updateDeco(), r2 = En(i2, n11, t3.changes);
    return e = it2.extendWithRanges(e, r2), this.dirty == 0 && e.length == 0 ? false : (this.updateInner(e, t3.startState.doc.length), t3.transactions.length && (this.lastUpdate = Date.now()), true);
  }
  updateInner(t3, e) {
    this.view.viewState.mustMeasureContent = true, this.updateChildren(t3, e);
    let { observer: i2 } = this.view;
    i2.ignore(() => {
      this.dom.style.height = this.view.viewState.contentHeight + "px", this.dom.style.flexBasis = this.minWidth ? this.minWidth + "px" : "";
      let r2 = g2.chrome || g2.ios ? {
        node: i2.selectionRange.focusNode,
        written: false
      } : void 0;
      this.sync(r2), this.dirty = 0, r2 && (r2.written || i2.selectionRange.focusNode != r2.node) && (this.forceSelection = true), this.dom.style.height = "";
    });
    let n11 = [];
    if (this.view.viewport.from || this.view.viewport.to < this.view.state.doc.length) for (let r2 of this.children) r2 instanceof Bt && r2.widget instanceof oe2 && n11.push(r2.dom);
    i2.updateGaps(n11);
  }
  updateChildren(t3, e) {
    let i2 = this.childCursor(e);
    for (let n11 = t3.length - 1; ; n11--) {
      let r2 = n11 >= 0 ? t3[n11] : null;
      if (!r2) break;
      let { fromA: o3, toA: l9, fromB: h, toB: a2 } = r2, { content: c3, breakAtStart: f, openStart: u2, openEnd: d } = We2.build(this.view.state.doc, h, a2, this.decorations, this.dynamicDecorationMap), { i: p2, off: m4 } = i2.findPos(l9, 1), { i: b4, off: y4 } = i2.findPos(o3, -1);
      ms(this, b4, y4, p2, m4, c3, f, u2, d);
    }
  }
  updateSelection(t3 = false, e = false) {
    if (t3 && this.view.observer.readSelectionRange(), !(e || this.mayControlSelection()) || g2.ios && this.view.inputState.rapidCompositionStart) return;
    let i2 = this.forceSelection;
    this.forceSelection = false;
    let n11 = this.view.state.selection.main, r2 = this.domAtPos(n11.anchor), o3 = n11.empty ? r2 : this.domAtPos(n11.head);
    if (g2.gecko && n11.empty && On(r2)) {
      let h = document.createTextNode("");
      this.view.observer.ignore(() => r2.node.insertBefore(h, r2.node.childNodes[r2.offset] || null)), r2 = o3 = new B2(h, 0), i2 = true;
    }
    let l9 = this.view.observer.selectionRange;
    (i2 || !l9.focusNode || !Ut(r2.node, r2.offset, l9.anchorNode, l9.anchorOffset) || !Ut(o3.node, o3.offset, l9.focusNode, l9.focusOffset)) && (this.view.observer.ignore(() => {
      g2.android && g2.chrome && this.dom.contains(l9.focusNode) && Bn(l9.focusNode, this.dom) && (this.dom.blur(), this.dom.focus({
        preventScroll: true
      }));
      let h = Yt(this.root);
      if (n11.empty) {
        if (g2.gecko) {
          let a2 = Ln(r2.node, r2.offset);
          if (a2 && a2 != 3) {
            let c3 = zs(r2.node, r2.offset, a2 == 1 ? 1 : -1);
            c3 && (r2 = new B2(c3, a2 == 1 ? 0 : c3.nodeValue.length));
          }
        }
        h.collapse(r2.node, r2.offset), n11.bidiLevel != null && l9.cursorBidiLevel != null && (l9.cursorBidiLevel = n11.bidiLevel);
      } else if (h.extend) h.collapse(r2.node, r2.offset), h.extend(o3.node, o3.offset);
      else {
        let a2 = document.createRange();
        n11.anchor > n11.head && ([r2, o3] = [
          o3,
          r2
        ]), a2.setEnd(o3.node, o3.offset), a2.setStart(r2.node, r2.offset), h.removeAllRanges(), h.addRange(a2);
      }
    }), this.view.observer.setSelectionRange(r2, o3)), this.impreciseAnchor = r2.precise ? null : new B2(l9.anchorNode, l9.anchorOffset), this.impreciseHead = o3.precise ? null : new B2(l9.focusNode, l9.focusOffset);
  }
  enforceCursorAssoc() {
    if (this.compositionDeco.size) return;
    let t3 = this.view.state.selection.main, e = Yt(this.root);
    if (!t3.empty || !t3.assoc || !e.modify) return;
    let i2 = N2.find(this, t3.head);
    if (!i2) return;
    let n11 = i2.posAtStart;
    if (t3.head == n11 || t3.head == n11 + i2.length) return;
    let r2 = this.coordsAt(t3.head, -1), o3 = this.coordsAt(t3.head, 1);
    if (!r2 || !o3 || r2.bottom > o3.top) return;
    let l9 = this.domAtPos(t3.head + t3.assoc);
    e.collapse(l9.node, l9.offset), e.modify("move", t3.assoc < 0 ? "forward" : "backward", "lineboundary");
  }
  mayControlSelection() {
    return this.view.state.facet(Nt) ? this.root.activeElement == this.dom : De2(this.dom, this.view.observer.selectionRange);
  }
  nearest(t3) {
    for (let e = t3; e; ) {
      let i2 = R2.get(e);
      if (i2 && i2.rootView == this) return i2;
      e = e.parentNode;
    }
    return null;
  }
  posFromDOM(t3, e) {
    let i2 = this.nearest(t3);
    if (!i2) throw new RangeError("Trying to find position for a DOM position outside of the document");
    return i2.localPosFromDOM(t3, e) + i2.posAtStart;
  }
  domAtPos(t3) {
    let { i: e, off: i2 } = this.childCursor().findPos(t3, -1);
    for (; e < this.children.length - 1; ) {
      let n11 = this.children[e];
      if (i2 < n11.length || n11 instanceof N2) break;
      e++, i2 = 0;
    }
    return this.children[e].domAtPos(i2);
  }
  coordsAt(t3, e) {
    for (let i2 = this.length, n11 = this.children.length - 1; ; n11--) {
      let r2 = this.children[n11], o3 = i2 - r2.breakAfter - r2.length;
      if (t3 > o3 || t3 == o3 && r2.type != D2.WidgetBefore && r2.type != D2.WidgetAfter && (!n11 || e == 2 || this.children[n11 - 1].breakAfter || this.children[n11 - 1].type == D2.WidgetBefore && e > -2)) return r2.coordsAt(t3 - o3, e);
      i2 = o3;
    }
  }
  measureVisibleLineHeights(t3) {
    let e = [], { from: i2, to: n11 } = t3, r2 = this.view.contentDOM.clientWidth, o3 = r2 > Math.max(this.view.scrollDOM.clientWidth, this.minWidth) + 1, l9 = -1, h = this.view.textDirection == O2.LTR;
    for (let a2 = 0, c3 = 0; c3 < this.children.length; c3++) {
      let f = this.children[c3], u2 = a2 + f.length;
      if (u2 > n11) break;
      if (a2 >= i2) {
        let d = f.dom.getBoundingClientRect();
        if (e.push(d.height), o3) {
          let p2 = f.dom.lastChild, m4 = p2 ? Tt(p2) : [];
          if (m4.length) {
            let b4 = m4[m4.length - 1], y4 = h ? b4.right - d.left : d.right - b4.left;
            y4 > l9 && (l9 = y4, this.minWidth = r2, this.minWidthFrom = a2, this.minWidthTo = u2);
          }
        }
      }
      a2 = u2 + f.breakAfter;
    }
    return e;
  }
  textDirectionAt(t3) {
    let { i: e } = this.childPos(t3, 1);
    return getComputedStyle(this.children[e].dom).direction == "rtl" ? O2.RTL : O2.LTR;
  }
  measureTextSize() {
    for (let n11 of this.children) if (n11 instanceof N2) {
      let r2 = n11.measureTextSize();
      if (r2) return r2;
    }
    let t3 = document.createElement("div"), e, i2;
    return t3.className = "cm-line", t3.textContent = "abc def ghi jkl mno pqr stu", this.view.observer.ignore(() => {
      this.dom.appendChild(t3);
      let n11 = Tt(t3.firstChild)[0];
      e = t3.getBoundingClientRect().height, i2 = n11 ? n11.width / 27 : 7, t3.remove();
    }), {
      lineHeight: e,
      charWidth: i2
    };
  }
  childCursor(t3 = this.length) {
    let e = this.children.length;
    return e && (t3 -= this.children[--e].length), new Jt(this.children, t3, e);
  }
  computeBlockGapDeco() {
    let t3 = [], e = this.view.viewState;
    for (let i2 = 0, n11 = 0; ; n11++) {
      let r2 = n11 == e.viewports.length ? null : e.viewports[n11], o3 = r2 ? r2.from - 1 : this.length;
      if (o3 > i2) {
        let l9 = e.lineBlockAt(o3).bottom - e.lineBlockAt(i2).top;
        t3.push(C2.replace({
          widget: new oe2(l9),
          block: true,
          inclusive: true,
          isBlockGap: true
        }).range(i2, o3));
      }
      if (!r2) break;
      i2 = r2.to + 1;
    }
    return C2.set(t3);
  }
  updateDeco() {
    let t3 = this.view.state.facet(Ht).map((e, i2) => (this.dynamicDecorationMap[i2] = typeof e == "function") ? e(this.view) : e);
    for (let e = t3.length; e < t3.length + 3; e++) this.dynamicDecorationMap[e] = false;
    return this.decorations = [
      ...t3,
      this.compositionDeco,
      this.computeBlockGapDeco(),
      this.view.viewState.lineGapDeco
    ];
  }
  scrollIntoView(t3) {
    let { range: e } = t3, i2 = this.coordsAt(e.head, e.empty ? e.assoc : e.head > e.anchor ? -1 : 1), n11;
    if (!i2) return;
    !e.empty && (n11 = this.coordsAt(e.anchor, e.anchor > e.head ? -1 : 1)) && (i2 = {
      left: Math.min(i2.left, n11.left),
      top: Math.min(i2.top, n11.top),
      right: Math.max(i2.right, n11.right),
      bottom: Math.max(i2.bottom, n11.bottom)
    });
    let r2 = 0, o3 = 0, l9 = 0, h = 0;
    for (let c3 of this.view.state.facet(Es).map((f) => f(this.view))) if (c3) {
      let { left: f, right: u2, top: d, bottom: p2 } = c3;
      f != null && (r2 = Math.max(r2, f)), u2 != null && (o3 = Math.max(o3, u2)), d != null && (l9 = Math.max(l9, d)), p2 != null && (h = Math.max(h, p2));
    }
    let a2 = {
      left: i2.left - r2,
      top: i2.top - l9,
      right: i2.right + o3,
      bottom: i2.bottom + h
    };
    yn(this.view.scrollDOM, a2, e.head < e.anchor ? -1 : 1, t3.x, t3.y, t3.xMargin, t3.yMargin, this.view.textDirection == O2.LTR);
  }
};
function On(s45) {
  return s45.node.nodeType == 1 && s45.node.firstChild && (s45.offset == 0 || s45.node.childNodes[s45.offset - 1].contentEditable == "false") && (s45.offset == s45.node.childNodes.length || s45.node.childNodes[s45.offset].contentEditable == "false");
}
var oe2 = class extends K2 {
  constructor(t3) {
    super(), this.height = t3;
  }
  toDOM() {
    let t3 = document.createElement("div");
    return this.updateDOM(t3), t3;
  }
  eq(t3) {
    return t3.height == this.height;
  }
  updateDOM(t3) {
    return t3.style.height = this.height + "px", true;
  }
  get estimatedHeight() {
    return this.height;
  }
};
function Ws(s45) {
  let t3 = s45.observer.selectionRange, e = t3.focusNode && zs(t3.focusNode, t3.focusOffset, 0);
  if (!e) return null;
  let i2 = s45.docView.nearest(e);
  if (!i2) return null;
  if (i2 instanceof N2) {
    let n11 = e;
    for (; n11.parentNode != i2.dom; ) n11 = n11.parentNode;
    let r2 = n11.previousSibling;
    for (; r2 && !R2.get(r2); ) r2 = r2.previousSibling;
    let o3 = r2 ? R2.get(r2).posAtEnd : i2.posAtStart;
    return {
      from: o3,
      to: o3,
      node: n11,
      text: e
    };
  } else {
    for (; ; ) {
      let { parent: r2 } = i2;
      if (!r2) return null;
      if (r2 instanceof N2) break;
      i2 = r2;
    }
    let n11 = i2.posAtStart;
    return {
      from: n11,
      to: n11 + i2.length,
      node: i2.dom,
      text: e
    };
  }
}
function Rn(s45, t3) {
  let e = Ws(s45);
  if (!e) return C2.none;
  let { from: i2, to: n11, node: r2, text: o3 } = e, l9 = t3.mapPos(i2, 1), h = Math.max(l9, t3.mapPos(n11, -1)), { state: a2 } = s45, c3 = r2.nodeType == 3 ? r2.nodeValue : new se2([], a2).readRange(r2.firstChild, null).text;
  if (h - l9 < c3.length) if (a2.doc.sliceString(l9, Math.min(a2.doc.length, l9 + c3.length), X2) == c3) h = l9 + c3.length;
  else if (a2.doc.sliceString(Math.max(0, h - c3.length), h, X2) == c3) l9 = h - c3.length;
  else return C2.none;
  else if (a2.doc.sliceString(l9, h, X2) != c3) return C2.none;
  let f = R2.get(r2);
  return f instanceof Zt ? f = f.widget.topView : f && (f.parent = null), C2.set(C2.replace({
    widget: new qe2(r2, o3, f),
    inclusive: true
  }).range(l9, h));
}
var qe2 = class extends K2 {
  constructor(t3, e, i2) {
    super(), this.top = t3, this.text = e, this.topView = i2;
  }
  eq(t3) {
    return this.top == t3.top && this.text == t3.text;
  }
  toDOM() {
    return this.top;
  }
  ignoreEvent() {
    return false;
  }
  get customView() {
    return Zt;
  }
};
function zs(s45, t3, e) {
  for (; ; ) {
    if (s45.nodeType == 3) return s45;
    if (s45.nodeType == 1 && t3 > 0 && e <= 0) s45 = s45.childNodes[t3 - 1], t3 = Xt(s45);
    else if (s45.nodeType == 1 && t3 < s45.childNodes.length && e >= 0) s45 = s45.childNodes[t3], t3 = 0;
    else return null;
  }
}
function Ln(s45, t3) {
  return s45.nodeType != 1 ? 0 : (t3 && s45.childNodes[t3 - 1].contentEditable == "false" ? 1 : 0) | (t3 < s45.childNodes.length && s45.childNodes[t3].contentEditable == "false" ? 2 : 0);
}
var Ke2 = class {
  constructor() {
    this.changes = [];
  }
  compareRange(t3, e) {
    Ne2(t3, e, this.changes);
  }
  comparePoint(t3, e) {
    Ne2(t3, e, this.changes);
  }
};
function En(s45, t3, e) {
  let i2 = new Ke2();
  return O.compare(s45, t3, e, i2), i2.changes;
}
function Bn(s45, t3) {
  for (let e = s45; e && e != t3; e = e.assignedSlot || e.parentNode) if (e.nodeType == 1 && e.contentEditable == "false") return true;
  return false;
}
function Hn(s45, t3, e = 1) {
  let i2 = s45.charCategorizer(t3), n11 = s45.doc.lineAt(t3), r2 = t3 - n11.from;
  if (n11.length == 0) return x.cursor(t3);
  r2 == 0 ? e = 1 : r2 == n11.length && (e = -1);
  let o3 = r2, l9 = r2;
  e < 0 ? o3 = _(n11.text, r2, false) : l9 = _(n11.text, r2);
  let h = i2(n11.text.slice(o3, l9));
  for (; o3 > 0; ) {
    let a2 = _(n11.text, o3, false);
    if (i2(n11.text.slice(a2, o3)) != h) break;
    o3 = a2;
  }
  for (; l9 < n11.length; ) {
    let a2 = _(n11.text, l9);
    if (i2(n11.text.slice(l9, a2)) != h) break;
    l9 = a2;
  }
  return x.range(o3 + n11.from, l9 + n11.from);
}
function Pn(s45, t3) {
  return t3.left > s45 ? t3.left - s45 : Math.max(0, s45 - t3.right);
}
function Vn(s45, t3) {
  return t3.top > s45 ? t3.top - s45 : Math.max(0, s45 - t3.bottom);
}
function we2(s45, t3) {
  return s45.top < t3.bottom - 1 && s45.bottom > t3.top + 1;
}
function Oi(s45, t3) {
  return t3 < s45.top ? {
    top: t3,
    left: s45.left,
    right: s45.right,
    bottom: s45.bottom
  } : s45;
}
function Ri(s45, t3) {
  return t3 > s45.bottom ? {
    top: s45.top,
    left: s45.left,
    right: s45.right,
    bottom: t3
  } : s45;
}
function je2(s45, t3, e) {
  let i2, n11, r2, o3, l9, h, a2, c3;
  for (let d = s45.firstChild; d; d = d.nextSibling) {
    let p2 = Tt(d);
    for (let m4 = 0; m4 < p2.length; m4++) {
      let b4 = p2[m4];
      n11 && we2(n11, b4) && (b4 = Oi(Ri(b4, n11.bottom), n11.top));
      let y4 = Pn(t3, b4), k4 = Vn(e, b4);
      if (y4 == 0 && k4 == 0) return d.nodeType == 3 ? Li(d, t3, e) : je2(d, t3, e);
      (!i2 || o3 > k4 || o3 == k4 && r2 > y4) && (i2 = d, n11 = b4, r2 = y4, o3 = k4), y4 == 0 ? e > b4.bottom && (!a2 || a2.bottom < b4.bottom) ? (l9 = d, a2 = b4) : e < b4.top && (!c3 || c3.top > b4.top) && (h = d, c3 = b4) : a2 && we2(a2, b4) ? a2 = Ri(a2, b4.bottom) : c3 && we2(c3, b4) && (c3 = Oi(c3, b4.top));
    }
  }
  if (a2 && a2.bottom >= e ? (i2 = l9, n11 = a2) : c3 && c3.top <= e && (i2 = h, n11 = c3), !i2) return {
    node: s45,
    offset: 0
  };
  let f = Math.max(n11.left, Math.min(n11.right, t3));
  if (i2.nodeType == 3) return Li(i2, f, e);
  if (!r2 && i2.contentEditable == "true") return je2(i2, f, e);
  let u2 = Array.prototype.indexOf.call(s45.childNodes, i2) + (t3 >= (n11.left + n11.right) / 2 ? 1 : 0);
  return {
    node: s45,
    offset: u2
  };
}
function Li(s45, t3, e) {
  let i2 = s45.nodeValue.length, n11 = -1, r2 = 1e9, o3 = 0;
  for (let l9 = 0; l9 < i2; l9++) {
    let h = Ot(s45, l9, l9 + 1).getClientRects();
    for (let a2 = 0; a2 < h.length; a2++) {
      let c3 = h[a2];
      if (c3.top == c3.bottom) continue;
      o3 || (o3 = t3 - c3.left);
      let f = (c3.top > e ? c3.top - e : e - c3.bottom) - 1;
      if (c3.left - 1 <= t3 && c3.right + 1 >= t3 && f < r2) {
        let u2 = t3 >= (c3.left + c3.right) / 2, d = u2;
        if ((g2.chrome || g2.gecko) && Ot(s45, l9).getBoundingClientRect().left == c3.right && (d = !u2), f <= 0) return {
          node: s45,
          offset: l9 + (d ? 1 : 0)
        };
        n11 = l9 + (d ? 1 : 0), r2 = f;
      }
    }
  }
  return {
    node: s45,
    offset: n11 > -1 ? n11 : o3 > 0 ? s45.nodeValue.length : 0
  };
}
function Fs(s45, { x: t3, y: e }, i2, n11 = -1) {
  var r2;
  let o3 = s45.contentDOM.getBoundingClientRect(), l9 = o3.top + s45.viewState.paddingTop, h, { docHeight: a2 } = s45.viewState, c3 = e - l9;
  if (c3 < 0) return 0;
  if (c3 > a2) return s45.state.doc.length;
  for (let y4 = s45.defaultLineHeight / 2, k4 = false; h = s45.elementAtHeight(c3), h.type != D2.Text; ) for (; c3 = n11 > 0 ? h.bottom + y4 : h.top - y4, !(c3 >= 0 && c3 <= a2); ) {
    if (k4) return i2 ? null : 0;
    k4 = true, n11 = -n11;
  }
  e = l9 + c3;
  let f = h.from;
  if (f < s45.viewport.from) return s45.viewport.from == 0 ? 0 : i2 ? null : Ei(s45, o3, h, t3, e);
  if (f > s45.viewport.to) return s45.viewport.to == s45.state.doc.length ? s45.state.doc.length : i2 ? null : Ei(s45, o3, h, t3, e);
  let u2 = s45.dom.ownerDocument, d = s45.root.elementFromPoint ? s45.root : u2, p2 = d.elementFromPoint(t3, e);
  p2 && !s45.contentDOM.contains(p2) && (p2 = null), p2 || (t3 = Math.max(o3.left + 1, Math.min(o3.right - 1, t3)), p2 = d.elementFromPoint(t3, e), p2 && !s45.contentDOM.contains(p2) && (p2 = null));
  let m4, b4 = -1;
  if (p2 && ((r2 = s45.docView.nearest(p2)) === null || r2 === void 0 ? void 0 : r2.isEditable) != false) {
    if (u2.caretPositionFromPoint) {
      let y4 = u2.caretPositionFromPoint(t3, e);
      y4 && ({ offsetNode: m4, offset: b4 } = y4);
    } else if (u2.caretRangeFromPoint) {
      let y4 = u2.caretRangeFromPoint(t3, e);
      y4 && ({ startContainer: m4, startOffset: b4 } = y4, g2.safari && Nn(m4, b4, t3) && (m4 = void 0));
    }
  }
  if (!m4 || !s45.docView.dom.contains(m4)) {
    let y4 = N2.find(s45.docView, f);
    if (!y4) return c3 > h.top + h.height / 2 ? h.to : h.from;
    ({ node: m4, offset: b4 } = je2(y4.dom, t3, e));
  }
  return s45.docView.posFromDOM(m4, b4);
}
function Ei(s45, t3, e, i2, n11) {
  let r2 = Math.round((i2 - t3.left) * s45.defaultCharacterWidth);
  if (s45.lineWrapping && e.height > s45.defaultLineHeight * 1.5) {
    let l9 = Math.floor((n11 - e.top) / s45.defaultLineHeight);
    r2 += l9 * s45.viewState.heightOracle.lineLength;
  }
  let o3 = s45.state.sliceDoc(e.from, e.to);
  return e.from + at(o3, r2, s45.state.tabSize);
}
function Nn(s45, t3, e) {
  let i2;
  if (s45.nodeType != 3 || t3 != (i2 = s45.nodeValue.length)) return false;
  for (let n11 = s45.nextSibling; n11; n11 = n11.nextSibling) if (n11.nodeType != 1 || n11.nodeName != "BR") return false;
  return Ot(s45, i2 - 1, i2).getBoundingClientRect().left > e;
}
function Wn(s45, t3, e, i2) {
  let n11 = s45.state.doc.lineAt(t3.head), r2 = !i2 || !s45.lineWrapping ? null : s45.coordsAtPos(t3.assoc < 0 && t3.head > n11.from ? t3.head - 1 : t3.head);
  if (r2) {
    let h = s45.dom.getBoundingClientRect(), a2 = s45.textDirectionAt(n11.from), c3 = s45.posAtCoords({
      x: e == (a2 == O2.LTR) ? h.right - 1 : h.left + 1,
      y: (r2.top + r2.bottom) / 2
    });
    if (c3 != null) return x.cursor(c3, e ? -1 : 1);
  }
  let o3 = N2.find(s45.docView, t3.head), l9 = o3 ? e ? o3.posAtEnd : o3.posAtStart : e ? n11.to : n11.from;
  return x.cursor(l9, e ? -1 : 1);
}
function Bi(s45, t3, e, i2) {
  let n11 = s45.state.doc.lineAt(t3.head), r2 = s45.bidiSpans(n11), o3 = s45.textDirectionAt(n11.from);
  for (let l9 = t3, h = null; ; ) {
    let a2 = Ns(n11, r2, o3, l9, e), c3 = Vs;
    if (!a2) {
      if (n11.number == (e ? s45.state.doc.lines : 1)) return l9;
      c3 = `
`, n11 = s45.state.doc.line(n11.number + (e ? 1 : -1)), r2 = s45.bidiSpans(n11), a2 = x.cursor(e ? n11.from : n11.to);
    }
    if (h) {
      if (!h(c3)) return l9;
    } else {
      if (!i2) return a2;
      h = i2(c3);
    }
    l9 = a2;
  }
}
function zn(s45, t3, e) {
  let i2 = s45.state.charCategorizer(t3), n11 = i2(e);
  return (r2) => {
    let o3 = i2(r2);
    return n11 == E.Space && (n11 = o3), n11 == o3;
  };
}
function Fn(s45, t3, e, i2) {
  let n11 = t3.head, r2 = e ? 1 : -1;
  if (n11 == (e ? s45.state.doc.length : 0)) return x.cursor(n11, t3.assoc);
  let o3 = t3.goalColumn, l9, h = s45.contentDOM.getBoundingClientRect(), a2 = s45.coordsAtPos(n11), c3 = s45.documentTop;
  if (a2) o3 == null && (o3 = a2.left - h.left), l9 = r2 < 0 ? a2.top : a2.bottom;
  else {
    let d = s45.viewState.lineBlockAt(n11);
    o3 == null && (o3 = Math.min(h.right - h.left, s45.defaultCharacterWidth * (n11 - d.from))), l9 = (r2 < 0 ? d.top : d.bottom) + c3;
  }
  let f = h.left + o3, u2 = i2 ?? s45.defaultLineHeight >> 1;
  for (let d = 0; ; d += 10) {
    let p2 = l9 + (u2 + d) * r2, m4 = Fs(s45, {
      x: f,
      y: p2
    }, false, r2);
    if (p2 < h.top || p2 > h.bottom || (r2 < 0 ? m4 < n11 : m4 > n11)) return x.cursor(m4, t3.assoc, void 0, o3);
  }
}
function ve2(s45, t3, e) {
  let i2 = s45.state.facet(Ls).map((n11) => n11(s45));
  for (; ; ) {
    let n11 = false;
    for (let r2 of i2) r2.between(e.from - 1, e.from + 1, (o3, l9, h) => {
      e.from > o3 && e.from < l9 && (e = t3.from > e.from ? x.cursor(o3, 1) : x.cursor(l9, -1), n11 = true);
    });
    if (!n11) return e;
  }
}
var Ge2 = class {
  constructor(t3) {
    this.lastKeyCode = 0, this.lastKeyTime = 0, this.chromeScrollHack = -1, this.pendingIOSKey = void 0, this.lastSelectionOrigin = null, this.lastSelectionTime = 0, this.lastEscPress = 0, this.lastContextMenu = 0, this.scrollHandlers = [], this.registeredEvents = [], this.customHandlers = [], this.composing = -1, this.compositionFirstChange = null, this.compositionEndedAt = 0, this.rapidCompositionStart = false, this.mouseSelection = null;
    for (let e in E2) {
      let i2 = E2[e];
      t3.contentDOM.addEventListener(e, (n11) => {
        !Hi(t3, n11) || this.ignoreDuringComposition(n11) || e == "keydown" && this.keydown(t3, n11) || (this.mustFlushObserver(n11) && t3.observer.forceFlush(), this.runCustomHandlers(e, t3, n11) ? n11.preventDefault() : i2(t3, n11));
      }), this.registeredEvents.push(e);
    }
    g2.chrome && g2.chrome_version >= 102 && t3.scrollDOM.addEventListener("wheel", () => {
      this.chromeScrollHack < 0 ? t3.contentDOM.style.pointerEvents = "none" : globalThis.clearTimeout(this.chromeScrollHack), this.chromeScrollHack = setTimeout(() => {
        this.chromeScrollHack = -1, t3.contentDOM.style.pointerEvents = "";
      }, 100);
    }, {
      passive: true
    }), this.notifiedFocused = t3.hasFocus, g2.safari && t3.contentDOM.addEventListener("input", () => null);
  }
  setSelectionOrigin(t3) {
    this.lastSelectionOrigin = t3, this.lastSelectionTime = Date.now();
  }
  ensureHandlers(t3, e) {
    var i2;
    let n11;
    this.customHandlers = [];
    for (let r2 of e) if (n11 = (i2 = r2.update(t3).spec) === null || i2 === void 0 ? void 0 : i2.domEventHandlers) {
      this.customHandlers.push({
        plugin: r2.value,
        handlers: n11
      });
      for (let o3 in n11) this.registeredEvents.indexOf(o3) < 0 && o3 != "scroll" && (this.registeredEvents.push(o3), t3.contentDOM.addEventListener(o3, (l9) => {
        Hi(t3, l9) && this.runCustomHandlers(o3, t3, l9) && l9.preventDefault();
      }));
    }
  }
  runCustomHandlers(t3, e, i2) {
    for (let n11 of this.customHandlers) {
      let r2 = n11.handlers[t3];
      if (r2) try {
        if (r2.call(n11.plugin, i2, e) || i2.defaultPrevented) return true;
      } catch (o3) {
        Z2(e.state, o3);
      }
    }
    return false;
  }
  runScrollHandlers(t3, e) {
    for (let i2 of this.customHandlers) {
      let n11 = i2.handlers.scroll;
      if (n11) try {
        n11.call(i2.plugin, e, t3);
      } catch (r2) {
        Z2(t3.state, r2);
      }
    }
  }
  keydown(t3, e) {
    if (this.lastKeyCode = e.keyCode, this.lastKeyTime = Date.now(), e.keyCode == 9 && Date.now() < this.lastEscPress + 2e3) return true;
    if (g2.android && g2.chrome && !e.synthetic && (e.keyCode == 13 || e.keyCode == 8)) return t3.observer.delayAndroidKey(e.key, e.keyCode), true;
    let i2;
    return g2.ios && (i2 = Is.find((n11) => n11.keyCode == e.keyCode)) && !(e.ctrlKey || e.altKey || e.metaKey) && !e.synthetic ? (this.pendingIOSKey = i2, setTimeout(() => this.flushIOSKey(t3), 250), true) : false;
  }
  flushIOSKey(t3) {
    let e = this.pendingIOSKey;
    return e ? (this.pendingIOSKey = void 0, Ct(t3.contentDOM, e.key, e.keyCode)) : false;
  }
  ignoreDuringComposition(t3) {
    return /^key/.test(t3.type) ? this.composing > 0 ? true : g2.safari && Date.now() - this.compositionEndedAt < 100 ? (this.compositionEndedAt = 0, true) : false : false;
  }
  mustFlushObserver(t3) {
    return t3.type == "keydown" && t3.keyCode != 229 || t3.type == "compositionend" && !g2.ios;
  }
  startMouseSelection(t3) {
    this.mouseSelection && this.mouseSelection.destroy(), this.mouseSelection = t3;
  }
  update(t3) {
    this.mouseSelection && this.mouseSelection.update(t3), t3.transactions.length && (this.lastKeyCode = this.lastSelectionTime = 0);
  }
  destroy() {
    this.mouseSelection && this.mouseSelection.destroy();
  }
};
var Is = [
  {
    key: "Backspace",
    keyCode: 8,
    inputType: "deleteContentBackward"
  },
  {
    key: "Enter",
    keyCode: 13,
    inputType: "insertParagraph"
  },
  {
    key: "Delete",
    keyCode: 46,
    inputType: "deleteContentForward"
  }
];
var qs = [
  16,
  17,
  18,
  20,
  91,
  92,
  224,
  225
];
var $e2 = class {
  constructor(t3, e, i2, n11) {
    this.view = t3, this.style = i2, this.mustSelect = n11, this.lastEvent = e;
    let r2 = t3.contentDOM.ownerDocument;
    r2.addEventListener("mousemove", this.move = this.move.bind(this)), r2.addEventListener("mouseup", this.up = this.up.bind(this)), this.extend = e.shiftKey, this.multiple = t3.state.facet(I.allowMultipleSelections) && In(t3, e), this.dragMove = qn(t3, e), this.dragging = Kn(t3, e) && yi(e) == 1 ? null : false, this.dragging === false && (e.preventDefault(), this.select(e));
  }
  move(t3) {
    if (t3.buttons == 0) return this.destroy();
    this.dragging === false && this.select(this.lastEvent = t3);
  }
  up(t3) {
    this.dragging == null && this.select(this.lastEvent), this.dragging || t3.preventDefault(), this.destroy();
  }
  destroy() {
    let t3 = this.view.contentDOM.ownerDocument;
    t3.removeEventListener("mousemove", this.move), t3.removeEventListener("mouseup", this.up), this.view.inputState.mouseSelection = null;
  }
  select(t3) {
    let e = this.style.get(t3, this.extend, this.multiple);
    (this.mustSelect || !e.eq(this.view.state.selection) || e.main.assoc != this.view.state.selection.main.assoc) && this.view.dispatch({
      selection: e,
      userEvent: "select.pointer",
      scrollIntoView: true
    }), this.mustSelect = false;
  }
  update(t3) {
    t3.docChanged && this.dragging && (this.dragging = this.dragging.map(t3.changes)), this.style.update(t3) && setTimeout(() => this.select(this.lastEvent), 20);
  }
};
function In(s45, t3) {
  let e = s45.state.facet(Ms);
  return e.length ? e[0](t3) : g2.mac ? t3.metaKey : t3.ctrlKey;
}
function qn(s45, t3) {
  let e = s45.state.facet(ks);
  return e.length ? e[0](t3) : g2.mac ? !t3.altKey : !t3.ctrlKey;
}
function Kn(s45, t3) {
  let { main: e } = s45.state.selection;
  if (e.empty) return false;
  let i2 = Yt(s45.root);
  if (i2.rangeCount == 0) return true;
  let n11 = i2.getRangeAt(0).getClientRects();
  for (let r2 = 0; r2 < n11.length; r2++) {
    let o3 = n11[r2];
    if (o3.left <= t3.clientX && o3.right >= t3.clientX && o3.top <= t3.clientY && o3.bottom >= t3.clientY) return true;
  }
  return false;
}
function Hi(s45, t3) {
  if (!t3.bubbles) return true;
  if (t3.defaultPrevented) return false;
  for (let e = t3.target, i2; e != s45.contentDOM; e = e.parentNode) if (!e || e.nodeType == 11 || (i2 = R2.get(e)) && i2.ignoreEvent(t3)) return false;
  return true;
}
var E2 = /* @__PURE__ */ Object.create(null);
var Ks = g2.ie && g2.ie_version < 15 || g2.ios && g2.webkit_version < 604;
function jn(s45) {
  let t3 = s45.dom.parentNode;
  if (!t3) return;
  let e = t3.appendChild(document.createElement("textarea"));
  e.style.cssText = "position: fixed; left: -10000px; top: 10px", e.focus(), setTimeout(() => {
    s45.focus(), e.remove(), js(s45, e.value);
  }, 50);
}
function js(s45, t3) {
  let { state: e } = s45, i2, n11 = 1, r2 = e.toText(t3), o3 = r2.lines == e.selection.ranges.length;
  if (_e2 != null && e.selection.ranges.every((h) => h.empty) && _e2 == r2.toString()) {
    let h = -1;
    i2 = e.changeByRange((a2) => {
      let c3 = e.doc.lineAt(a2.from);
      if (c3.from == h) return {
        range: a2
      };
      h = c3.from;
      let f = e.toText((o3 ? r2.line(n11++).text : t3) + e.lineBreak);
      return {
        changes: {
          from: c3.from,
          insert: f
        },
        range: x.cursor(a2.from + f.length)
      };
    });
  } else o3 ? i2 = e.changeByRange((h) => {
    let a2 = r2.line(n11++);
    return {
      changes: {
        from: h.from,
        to: h.to,
        insert: a2.text
      },
      range: x.cursor(h.from + a2.length)
    };
  }) : i2 = e.replaceSelection(r2);
  s45.dispatch(i2, {
    userEvent: "input.paste",
    scrollIntoView: true
  });
}
E2.keydown = (s45, t3) => {
  s45.inputState.setSelectionOrigin("select"), t3.keyCode == 27 ? s45.inputState.lastEscPress = Date.now() : qs.indexOf(t3.keyCode) < 0 && (s45.inputState.lastEscPress = 0);
};
var Gs = 0;
E2.touchstart = (s45, t3) => {
  Gs = Date.now(), s45.inputState.setSelectionOrigin("select.pointer");
};
E2.touchmove = (s45) => {
  s45.inputState.setSelectionOrigin("select.pointer");
};
E2.mousedown = (s45, t3) => {
  if (s45.observer.flush(), Gs > Date.now() - 2e3 && yi(t3) == 1) return;
  let e = null;
  for (let i2 of s45.state.facet(As)) if (e = i2(s45, t3), e) break;
  if (!e && t3.button == 0 && (e = _n(s45, t3)), e) {
    let i2 = s45.root.activeElement != s45.contentDOM;
    i2 && s45.observer.ignore(() => us(s45.contentDOM)), s45.inputState.startMouseSelection(new $e2(s45, t3, e, i2));
  }
};
function Pi(s45, t3, e, i2) {
  if (i2 == 1) return x.cursor(t3, e);
  if (i2 == 2) return Hn(s45.state, t3, e);
  {
    let n11 = N2.find(s45.docView, t3), r2 = s45.state.doc.lineAt(n11 ? n11.posAtEnd : t3), o3 = n11 ? n11.posAtStart : r2.from, l9 = n11 ? n11.posAtEnd : r2.to;
    return l9 < s45.state.doc.length && l9 == r2.to && l9++, x.range(o3, l9);
  }
}
var $s = (s45, t3) => s45 >= t3.top && s45 <= t3.bottom;
var Vi = (s45, t3, e) => $s(t3, e) && s45 >= e.left && s45 <= e.right;
function Gn(s45, t3, e, i2) {
  let n11 = N2.find(s45.docView, t3);
  if (!n11) return 1;
  let r2 = t3 - n11.posAtStart;
  if (r2 == 0) return 1;
  if (r2 == n11.length) return -1;
  let o3 = n11.coordsAt(r2, -1);
  if (o3 && Vi(e, i2, o3)) return -1;
  let l9 = n11.coordsAt(r2, 1);
  return l9 && Vi(e, i2, l9) ? 1 : o3 && $s(i2, o3) ? -1 : 1;
}
function Ni(s45, t3) {
  let e = s45.posAtCoords({
    x: t3.clientX,
    y: t3.clientY
  }, false);
  return {
    pos: e,
    bias: Gn(s45, e, t3.clientX, t3.clientY)
  };
}
var $n = g2.ie && g2.ie_version <= 11;
var Wi = null;
var zi = 0;
var Fi = 0;
function yi(s45) {
  if (!$n) return s45.detail;
  let t3 = Wi, e = Fi;
  return Wi = s45, Fi = Date.now(), zi = !t3 || e > Date.now() - 400 && Math.abs(t3.clientX - s45.clientX) < 2 && Math.abs(t3.clientY - s45.clientY) < 2 ? (zi + 1) % 3 : 1;
}
function _n(s45, t3) {
  let e = Ni(s45, t3), i2 = yi(t3), n11 = s45.state.selection, r2 = e, o3 = t3;
  return {
    update(l9) {
      l9.docChanged && (e && (e.pos = l9.changes.mapPos(e.pos)), n11 = n11.map(l9.changes), o3 = null);
    },
    get(l9, h, a2) {
      let c3;
      if (o3 && l9.clientX == o3.clientX && l9.clientY == o3.clientY ? c3 = r2 : (c3 = r2 = Ni(s45, l9), o3 = l9), !c3 || !e) return n11;
      let f = Pi(s45, c3.pos, c3.bias, i2);
      if (e.pos != c3.pos && !h) {
        let u2 = Pi(s45, e.pos, e.bias, i2), d = Math.min(u2.from, f.from), p2 = Math.max(u2.to, f.to);
        f = d < f.from ? x.range(d, p2) : x.range(p2, d);
      }
      return h ? n11.replaceRange(n11.main.extend(f.from, f.to)) : a2 ? n11.addRange(f) : x.create([
        f
      ]);
    }
  };
}
E2.dragstart = (s45, t3) => {
  let { selection: { main: e } } = s45.state, { mouseSelection: i2 } = s45.inputState;
  i2 && (i2.dragging = e), t3.dataTransfer && (t3.dataTransfer.setData("Text", s45.state.sliceDoc(e.from, e.to)), t3.dataTransfer.effectAllowed = "copyMove");
};
function Ii(s45, t3, e, i2) {
  if (!e) return;
  let n11 = s45.posAtCoords({
    x: t3.clientX,
    y: t3.clientY
  }, false);
  t3.preventDefault();
  let { mouseSelection: r2 } = s45.inputState, o3 = i2 && r2 && r2.dragging && r2.dragMove ? {
    from: r2.dragging.from,
    to: r2.dragging.to
  } : null, l9 = {
    from: n11,
    insert: e
  }, h = s45.state.changes(o3 ? [
    o3,
    l9
  ] : l9);
  s45.focus(), s45.dispatch({
    changes: h,
    selection: {
      anchor: h.mapPos(n11, -1),
      head: h.mapPos(n11, 1)
    },
    userEvent: o3 ? "move.drop" : "input.drop"
  });
}
E2.drop = (s45, t3) => {
  if (!t3.dataTransfer) return;
  if (s45.state.readOnly) return t3.preventDefault();
  let e = t3.dataTransfer.files;
  if (e && e.length) {
    t3.preventDefault();
    let i2 = Array(e.length), n11 = 0, r2 = () => {
      ++n11 == e.length && Ii(s45, t3, i2.filter((o3) => o3 != null).join(s45.state.lineBreak), false);
    };
    for (let o3 = 0; o3 < e.length; o3++) {
      let l9 = new FileReader();
      l9.onerror = r2, l9.onload = () => {
        /[\x00-\x08\x0e-\x1f]{2}/.test(l9.result) || (i2[o3] = l9.result), r2();
      }, l9.readAsText(e[o3]);
    }
  } else Ii(s45, t3, t3.dataTransfer.getData("Text"), true);
};
E2.paste = (s45, t3) => {
  if (s45.state.readOnly) return t3.preventDefault();
  s45.observer.flush();
  let e = Ks ? null : t3.clipboardData;
  e ? (js(s45, e.getData("text/plain")), t3.preventDefault()) : jn(s45);
};
function Yn(s45, t3) {
  let e = s45.dom.parentNode;
  if (!e) return;
  let i2 = e.appendChild(document.createElement("textarea"));
  i2.style.cssText = "position: fixed; left: -10000px; top: 10px", i2.value = t3, i2.focus(), i2.selectionEnd = t3.length, i2.selectionStart = 0, setTimeout(() => {
    i2.remove(), s45.focus();
  }, 50);
}
function Un(s45) {
  let t3 = [], e = [], i2 = false;
  for (let n11 of s45.selection.ranges) n11.empty || (t3.push(s45.sliceDoc(n11.from, n11.to)), e.push(n11));
  if (!t3.length) {
    let n11 = -1;
    for (let { from: r2 } of s45.selection.ranges) {
      let o3 = s45.doc.lineAt(r2);
      o3.number > n11 && (t3.push(o3.text), e.push({
        from: o3.from,
        to: Math.min(s45.doc.length, o3.to + 1)
      })), n11 = o3.number;
    }
    i2 = true;
  }
  return {
    text: t3.join(s45.lineBreak),
    ranges: e,
    linewise: i2
  };
}
var _e2 = null;
E2.copy = E2.cut = (s45, t3) => {
  let { text: e, ranges: i2, linewise: n11 } = Un(s45.state);
  if (!e && !n11) return;
  _e2 = n11 ? e : null;
  let r2 = Ks ? null : t3.clipboardData;
  r2 ? (t3.preventDefault(), r2.clearData(), r2.setData("text/plain", e)) : Yn(s45, e), t3.type == "cut" && !s45.state.readOnly && s45.dispatch({
    changes: i2,
    scrollIntoView: true,
    userEvent: "delete.cut"
  });
};
function _s(s45) {
  setTimeout(() => {
    s45.hasFocus != s45.inputState.notifiedFocused && s45.update([]);
  }, 10);
}
E2.focus = _s;
E2.blur = (s45) => {
  s45.observer.clearSelectionRange(), _s(s45);
};
function Ys(s45, t3) {
  if (s45.docView.compositionDeco.size) {
    s45.inputState.rapidCompositionStart = t3;
    try {
      s45.update([]);
    } finally {
      s45.inputState.rapidCompositionStart = false;
    }
  }
}
E2.compositionstart = E2.compositionupdate = (s45) => {
  s45.inputState.compositionFirstChange == null && (s45.inputState.compositionFirstChange = true), s45.inputState.composing < 0 && (s45.inputState.composing = 0, s45.docView.compositionDeco.size && (s45.observer.flush(), Ys(s45, true)));
};
E2.compositionend = (s45) => {
  s45.inputState.composing = -1, s45.inputState.compositionEndedAt = Date.now(), s45.inputState.compositionFirstChange = null, setTimeout(() => {
    s45.inputState.composing < 0 && Ys(s45, false);
  }, 50);
};
E2.contextmenu = (s45) => {
  s45.inputState.lastContextMenu = Date.now();
};
E2.beforeinput = (s45, t3) => {
  var e;
  let i2;
  if (g2.chrome && g2.android && (i2 = Is.find((n11) => n11.inputType == t3.inputType)) && (s45.observer.delayAndroidKey(i2.key, i2.keyCode), i2.key == "Backspace" || i2.key == "Delete")) {
    let n11 = ((e = globalThis.visualViewport) === null || e === void 0 ? void 0 : e.height) || 0;
    setTimeout(() => {
      var r2;
      (((r2 = globalThis.visualViewport) === null || r2 === void 0 ? void 0 : r2.height) || 0) > n11 + 10 && s45.hasFocus && (s45.contentDOM.blur(), s45.focus());
    }, 100);
  }
};
var qi = [
  "pre-wrap",
  "normal",
  "pre-line",
  "break-spaces"
];
var le = class {
  constructor() {
    this.doc = m.empty, this.lineWrapping = false, this.heightSamples = {}, this.lineHeight = 14, this.charWidth = 7, this.lineLength = 30, this.heightChanged = false;
  }
  heightForGap(t3, e) {
    let i2 = this.doc.lineAt(e).number - this.doc.lineAt(t3).number + 1;
    return this.lineWrapping && (i2 += Math.ceil((e - t3 - i2 * this.lineLength * 0.5) / this.lineLength)), this.lineHeight * i2;
  }
  heightForLine(t3) {
    return this.lineWrapping ? (1 + Math.max(0, Math.ceil((t3 - this.lineLength) / (this.lineLength - 5)))) * this.lineHeight : this.lineHeight;
  }
  setDoc(t3) {
    return this.doc = t3, this;
  }
  mustRefreshForWrapping(t3) {
    return qi.indexOf(t3) > -1 != this.lineWrapping;
  }
  mustRefreshForHeights(t3) {
    let e = false;
    for (let i2 = 0; i2 < t3.length; i2++) {
      let n11 = t3[i2];
      n11 < 0 ? i2++ : this.heightSamples[Math.floor(n11 * 10)] || (e = true, this.heightSamples[Math.floor(n11 * 10)] = true);
    }
    return e;
  }
  refresh(t3, e, i2, n11, r2) {
    let o3 = qi.indexOf(t3) > -1, l9 = Math.round(e) != Math.round(this.lineHeight) || this.lineWrapping != o3;
    if (this.lineWrapping = o3, this.lineHeight = e, this.charWidth = i2, this.lineLength = n11, l9) {
      this.heightSamples = {};
      for (let h = 0; h < r2.length; h++) {
        let a2 = r2[h];
        a2 < 0 ? h++ : this.heightSamples[Math.floor(a2 * 10)] = true;
      }
    }
    return l9;
  }
};
var he2 = class {
  constructor(t3, e) {
    this.from = t3, this.heights = e, this.index = 0;
  }
  get more() {
    return this.index < this.heights.length;
  }
};
var J2 = class s36 {
  constructor(t3, e, i2, n11, r2) {
    this.from = t3, this.length = e, this.top = i2, this.height = n11, this.type = r2;
  }
  get to() {
    return this.from + this.length;
  }
  get bottom() {
    return this.top + this.height;
  }
  join(t3) {
    let e = (Array.isArray(this.type) ? this.type : [
      this
    ]).concat(Array.isArray(t3.type) ? t3.type : [
      t3
    ]);
    return new s36(this.from, this.length + t3.length, this.top, this.height + t3.height, e);
  }
};
var A = function(s45) {
  return s45[s45.ByPos = 0] = "ByPos", s45[s45.ByHeight = 1] = "ByHeight", s45[s45.ByPosNoHeight = 2] = "ByPosNoHeight", s45;
}(A || (A = {}));
var jt = 1e-3;
var W2 = class s37 {
  constructor(t3, e, i2 = 2) {
    this.length = t3, this.height = e, this.flags = i2;
  }
  get outdated() {
    return (this.flags & 2) > 0;
  }
  set outdated(t3) {
    this.flags = (t3 ? 2 : 0) | this.flags & -3;
  }
  setHeight(t3, e) {
    this.height != e && (Math.abs(this.height - e) > jt && (t3.heightChanged = true), this.height = e);
  }
  replace(t3, e, i2) {
    return s37.of(i2);
  }
  decomposeLeft(t3, e) {
    e.push(this);
  }
  decomposeRight(t3, e) {
    e.push(this);
  }
  applyChanges(t3, e, i2, n11) {
    let r2 = this;
    for (let o3 = n11.length - 1; o3 >= 0; o3--) {
      let { fromA: l9, toA: h, fromB: a2, toB: c3 } = n11[o3], f = r2.lineAt(l9, A.ByPosNoHeight, e, 0, 0), u2 = f.to >= h ? f : r2.lineAt(h, A.ByPosNoHeight, e, 0, 0);
      for (c3 += u2.to - h, h = u2.to; o3 > 0 && f.from <= n11[o3 - 1].toA; ) l9 = n11[o3 - 1].fromA, a2 = n11[o3 - 1].fromB, o3--, l9 < f.from && (f = r2.lineAt(l9, A.ByPosNoHeight, e, 0, 0));
      a2 += f.from - l9, l9 = f.from;
      let d = Ue2.build(i2, t3, a2, c3);
      r2 = r2.replace(l9, h, d);
    }
    return r2.updateHeight(i2, 0);
  }
  static empty() {
    return new z2(0, 0);
  }
  static of(t3) {
    if (t3.length == 1) return t3[0];
    let e = 0, i2 = t3.length, n11 = 0, r2 = 0;
    for (; ; ) if (e == i2) if (n11 > r2 * 2) {
      let l9 = t3[e - 1];
      l9.break ? t3.splice(--e, 1, l9.left, null, l9.right) : t3.splice(--e, 1, l9.left, l9.right), i2 += 1 + l9.break, n11 -= l9.size;
    } else if (r2 > n11 * 2) {
      let l9 = t3[i2];
      l9.break ? t3.splice(i2, 1, l9.left, null, l9.right) : t3.splice(i2, 1, l9.left, l9.right), i2 += 2 + l9.break, r2 -= l9.size;
    } else break;
    else if (n11 < r2) {
      let l9 = t3[e++];
      l9 && (n11 += l9.size);
    } else {
      let l9 = t3[--i2];
      l9 && (r2 += l9.size);
    }
    let o3 = 0;
    return t3[e - 1] == null ? (o3 = 1, e--) : t3[e] == null && (o3 = 1, i2++), new Ye2(s37.of(t3.slice(0, e)), o3, s37.of(t3.slice(i2)));
  }
};
W2.prototype.size = 1;
var ae2 = class extends W2 {
  constructor(t3, e, i2) {
    super(t3, e), this.type = i2;
  }
  blockAt(t3, e, i2, n11) {
    return new J2(n11, this.length, i2, this.height, this.type);
  }
  lineAt(t3, e, i2, n11, r2) {
    return this.blockAt(0, i2, n11, r2);
  }
  forEachLine(t3, e, i2, n11, r2, o3) {
    t3 <= r2 + this.length && e >= r2 && o3(this.blockAt(0, i2, n11, r2));
  }
  updateHeight(t3, e = 0, i2 = false, n11) {
    return n11 && n11.from <= e && n11.more && this.setHeight(t3, n11.heights[n11.index++]), this.outdated = false, this;
  }
  toString() {
    return `block(${this.length})`;
  }
};
var z2 = class s38 extends ae2 {
  constructor(t3, e) {
    super(t3, e, D2.Text), this.collapsed = 0, this.widgetHeight = 0;
  }
  replace(t3, e, i2) {
    let n11 = i2[0];
    return i2.length == 1 && (n11 instanceof s38 || n11 instanceof tt2 && n11.flags & 4) && Math.abs(this.length - n11.length) < 10 ? (n11 instanceof tt2 ? n11 = new s38(n11.length, this.height) : n11.height = this.height, this.outdated || (n11.outdated = false), n11) : W2.of(i2);
  }
  updateHeight(t3, e = 0, i2 = false, n11) {
    return n11 && n11.from <= e && n11.more ? this.setHeight(t3, n11.heights[n11.index++]) : (i2 || this.outdated) && this.setHeight(t3, Math.max(this.widgetHeight, t3.heightForLine(this.length - this.collapsed))), this.outdated = false, this;
  }
  toString() {
    return `line(${this.length}${this.collapsed ? -this.collapsed : ""}${this.widgetHeight ? ":" + this.widgetHeight : ""})`;
  }
};
var tt2 = class s39 extends W2 {
  constructor(t3) {
    super(t3, 0);
  }
  lines(t3, e) {
    let i2 = t3.lineAt(e).number, n11 = t3.lineAt(e + this.length).number;
    return {
      firstLine: i2,
      lastLine: n11,
      lineHeight: this.height / (n11 - i2 + 1)
    };
  }
  blockAt(t3, e, i2, n11) {
    let { firstLine: r2, lastLine: o3, lineHeight: l9 } = this.lines(e, n11), h = Math.max(0, Math.min(o3 - r2, Math.floor((t3 - i2) / l9))), { from: a2, length: c3 } = e.line(r2 + h);
    return new J2(a2, c3, i2 + l9 * h, l9, D2.Text);
  }
  lineAt(t3, e, i2, n11, r2) {
    if (e == A.ByHeight) return this.blockAt(t3, i2, n11, r2);
    if (e == A.ByPosNoHeight) {
      let { from: f, to: u2 } = i2.lineAt(t3);
      return new J2(f, u2 - f, 0, 0, D2.Text);
    }
    let { firstLine: o3, lineHeight: l9 } = this.lines(i2, r2), { from: h, length: a2, number: c3 } = i2.lineAt(t3);
    return new J2(h, a2, n11 + l9 * (c3 - o3), l9, D2.Text);
  }
  forEachLine(t3, e, i2, n11, r2, o3) {
    let { firstLine: l9, lineHeight: h } = this.lines(i2, r2);
    for (let a2 = Math.max(t3, r2), c3 = Math.min(r2 + this.length, e); a2 <= c3; ) {
      let f = i2.lineAt(a2);
      a2 == t3 && (n11 += h * (f.number - l9)), o3(new J2(f.from, f.length, n11, h, D2.Text)), n11 += h, a2 = f.to + 1;
    }
  }
  replace(t3, e, i2) {
    let n11 = this.length - e;
    if (n11 > 0) {
      let r2 = i2[i2.length - 1];
      r2 instanceof s39 ? i2[i2.length - 1] = new s39(r2.length + n11) : i2.push(null, new s39(n11 - 1));
    }
    if (t3 > 0) {
      let r2 = i2[0];
      r2 instanceof s39 ? i2[0] = new s39(t3 + r2.length) : i2.unshift(new s39(t3 - 1), null);
    }
    return W2.of(i2);
  }
  decomposeLeft(t3, e) {
    e.push(new s39(t3 - 1), null);
  }
  decomposeRight(t3, e) {
    e.push(null, new s39(this.length - t3 - 1));
  }
  updateHeight(t3, e = 0, i2 = false, n11) {
    let r2 = e + this.length;
    if (n11 && n11.from <= e + this.length && n11.more) {
      let o3 = [], l9 = Math.max(e, n11.from), h = -1, a2 = t3.heightChanged;
      for (n11.from > e && o3.push(new s39(n11.from - e - 1).updateHeight(t3, e)); l9 <= r2 && n11.more; ) {
        let f = t3.doc.lineAt(l9).length;
        o3.length && o3.push(null);
        let u2 = n11.heights[n11.index++];
        h == -1 ? h = u2 : Math.abs(u2 - h) >= jt && (h = -2);
        let d = new z2(f, u2);
        d.outdated = false, o3.push(d), l9 += f + 1;
      }
      l9 <= r2 && o3.push(null, new s39(r2 - l9).updateHeight(t3, l9));
      let c3 = W2.of(o3);
      return t3.heightChanged = a2 || h < 0 || Math.abs(c3.height - this.height) >= jt || Math.abs(h - this.lines(t3.doc, e).lineHeight) >= jt, c3;
    } else (i2 || this.outdated) && (this.setHeight(t3, t3.heightForGap(e, e + this.length)), this.outdated = false);
    return this;
  }
  toString() {
    return `gap(${this.length})`;
  }
};
var Ye2 = class extends W2 {
  constructor(t3, e, i2) {
    super(t3.length + e + i2.length, t3.height + i2.height, e | (t3.outdated || i2.outdated ? 2 : 0)), this.left = t3, this.right = i2, this.size = t3.size + i2.size;
  }
  get break() {
    return this.flags & 1;
  }
  blockAt(t3, e, i2, n11) {
    let r2 = i2 + this.left.height;
    return t3 < r2 ? this.left.blockAt(t3, e, i2, n11) : this.right.blockAt(t3, e, r2, n11 + this.left.length + this.break);
  }
  lineAt(t3, e, i2, n11, r2) {
    let o3 = n11 + this.left.height, l9 = r2 + this.left.length + this.break, h = e == A.ByHeight ? t3 < o3 : t3 < l9, a2 = h ? this.left.lineAt(t3, e, i2, n11, r2) : this.right.lineAt(t3, e, i2, o3, l9);
    if (this.break || (h ? a2.to < l9 : a2.from > l9)) return a2;
    let c3 = e == A.ByPosNoHeight ? A.ByPosNoHeight : A.ByPos;
    return h ? a2.join(this.right.lineAt(l9, c3, i2, o3, l9)) : this.left.lineAt(l9, c3, i2, n11, r2).join(a2);
  }
  forEachLine(t3, e, i2, n11, r2, o3) {
    let l9 = n11 + this.left.height, h = r2 + this.left.length + this.break;
    if (this.break) t3 < h && this.left.forEachLine(t3, e, i2, n11, r2, o3), e >= h && this.right.forEachLine(t3, e, i2, l9, h, o3);
    else {
      let a2 = this.lineAt(h, A.ByPos, i2, n11, r2);
      t3 < a2.from && this.left.forEachLine(t3, a2.from - 1, i2, n11, r2, o3), a2.to >= t3 && a2.from <= e && o3(a2), e > a2.to && this.right.forEachLine(a2.to + 1, e, i2, l9, h, o3);
    }
  }
  replace(t3, e, i2) {
    let n11 = this.left.length + this.break;
    if (e < n11) return this.balanced(this.left.replace(t3, e, i2), this.right);
    if (t3 > this.left.length) return this.balanced(this.left, this.right.replace(t3 - n11, e - n11, i2));
    let r2 = [];
    t3 > 0 && this.decomposeLeft(t3, r2);
    let o3 = r2.length;
    for (let l9 of i2) r2.push(l9);
    if (t3 > 0 && Ki(r2, o3 - 1), e < this.length) {
      let l9 = r2.length;
      this.decomposeRight(e, r2), Ki(r2, l9);
    }
    return W2.of(r2);
  }
  decomposeLeft(t3, e) {
    let i2 = this.left.length;
    if (t3 <= i2) return this.left.decomposeLeft(t3, e);
    e.push(this.left), this.break && (i2++, t3 >= i2 && e.push(null)), t3 > i2 && this.right.decomposeLeft(t3 - i2, e);
  }
  decomposeRight(t3, e) {
    let i2 = this.left.length, n11 = i2 + this.break;
    if (t3 >= n11) return this.right.decomposeRight(t3 - n11, e);
    t3 < i2 && this.left.decomposeRight(t3, e), this.break && t3 < n11 && e.push(null), e.push(this.right);
  }
  balanced(t3, e) {
    return t3.size > 2 * e.size || e.size > 2 * t3.size ? W2.of(this.break ? [
      t3,
      null,
      e
    ] : [
      t3,
      e
    ]) : (this.left = t3, this.right = e, this.height = t3.height + e.height, this.outdated = t3.outdated || e.outdated, this.size = t3.size + e.size, this.length = t3.length + this.break + e.length, this);
  }
  updateHeight(t3, e = 0, i2 = false, n11) {
    let { left: r2, right: o3 } = this, l9 = e + r2.length + this.break, h = null;
    return n11 && n11.from <= e + r2.length && n11.more ? h = r2 = r2.updateHeight(t3, e, i2, n11) : r2.updateHeight(t3, e, i2), n11 && n11.from <= l9 + o3.length && n11.more ? h = o3 = o3.updateHeight(t3, l9, i2, n11) : o3.updateHeight(t3, l9, i2), h ? this.balanced(r2, o3) : (this.height = this.left.height + this.right.height, this.outdated = false, this);
  }
  toString() {
    return this.left + (this.break ? " " : "-") + this.right;
  }
};
function Ki(s45, t3) {
  let e, i2;
  s45[t3] == null && (e = s45[t3 - 1]) instanceof tt2 && (i2 = s45[t3 + 1]) instanceof tt2 && s45.splice(t3 - 1, 3, new tt2(e.length + 1 + i2.length));
}
var Xn = 5;
var Ue2 = class s40 {
  constructor(t3, e) {
    this.pos = t3, this.oracle = e, this.nodes = [], this.lineStart = -1, this.lineEnd = -1, this.covering = null, this.writtenTo = t3;
  }
  get isCovered() {
    return this.covering && this.nodes[this.nodes.length - 1] == this.covering;
  }
  span(t3, e) {
    if (this.lineStart > -1) {
      let i2 = Math.min(e, this.lineEnd), n11 = this.nodes[this.nodes.length - 1];
      n11 instanceof z2 ? n11.length += i2 - this.pos : (i2 > this.pos || !this.isCovered) && this.nodes.push(new z2(i2 - this.pos, -1)), this.writtenTo = i2, e > i2 && (this.nodes.push(null), this.writtenTo++, this.lineStart = -1);
    }
    this.pos = e;
  }
  point(t3, e, i2) {
    if (t3 < e || i2.heightRelevant) {
      let n11 = i2.widget ? i2.widget.estimatedHeight : 0;
      n11 < 0 && (n11 = this.oracle.lineHeight);
      let r2 = e - t3;
      i2.block ? this.addBlock(new ae2(r2, n11, i2.type)) : (r2 || n11 >= Xn) && this.addLineDeco(n11, r2);
    } else e > t3 && this.span(t3, e);
    this.lineEnd > -1 && this.lineEnd < this.pos && (this.lineEnd = this.oracle.doc.lineAt(this.pos).to);
  }
  enterLine() {
    if (this.lineStart > -1) return;
    let { from: t3, to: e } = this.oracle.doc.lineAt(this.pos);
    this.lineStart = t3, this.lineEnd = e, this.writtenTo < t3 && ((this.writtenTo < t3 - 1 || this.nodes[this.nodes.length - 1] == null) && this.nodes.push(this.blankContent(this.writtenTo, t3 - 1)), this.nodes.push(null)), this.pos > t3 && this.nodes.push(new z2(this.pos - t3, -1)), this.writtenTo = this.pos;
  }
  blankContent(t3, e) {
    let i2 = new tt2(e - t3);
    return this.oracle.doc.lineAt(t3).to == e && (i2.flags |= 4), i2;
  }
  ensureLine() {
    this.enterLine();
    let t3 = this.nodes.length ? this.nodes[this.nodes.length - 1] : null;
    if (t3 instanceof z2) return t3;
    let e = new z2(0, -1);
    return this.nodes.push(e), e;
  }
  addBlock(t3) {
    this.enterLine(), t3.type == D2.WidgetAfter && !this.isCovered && this.ensureLine(), this.nodes.push(t3), this.writtenTo = this.pos = this.pos + t3.length, t3.type != D2.WidgetBefore && (this.covering = t3);
  }
  addLineDeco(t3, e) {
    let i2 = this.ensureLine();
    i2.length += e, i2.collapsed += e, i2.widgetHeight = Math.max(i2.widgetHeight, t3), this.writtenTo = this.pos = this.pos + e;
  }
  finish(t3) {
    let e = this.nodes.length == 0 ? null : this.nodes[this.nodes.length - 1];
    this.lineStart > -1 && !(e instanceof z2) && !this.isCovered ? this.nodes.push(new z2(0, -1)) : (this.writtenTo < this.pos || e == null) && this.nodes.push(this.blankContent(this.writtenTo, this.pos));
    let i2 = t3;
    for (let n11 of this.nodes) n11 instanceof z2 && n11.updateHeight(this.oracle, i2), i2 += n11 ? n11.length : 1;
    return this.nodes;
  }
  static build(t3, e, i2, n11) {
    let r2 = new s40(i2, t3);
    return O.spans(e, i2, n11, r2, 0), r2.finish(i2);
  }
};
function Jn(s45, t3, e) {
  let i2 = new Xe2();
  return O.compare(s45, t3, e, i2, 0), i2.changes;
}
var Xe2 = class {
  constructor() {
    this.changes = [];
  }
  compareRange() {
  }
  comparePoint(t3, e, i2, n11) {
    (t3 < e || i2 && i2.heightRelevant || n11 && n11.heightRelevant) && Ne2(t3, e, this.changes, 5);
  }
};
function Zn(s45, t3) {
  let e = s45.getBoundingClientRect(), i2 = Math.max(0, e.left), n11 = Math.min(innerWidth, e.right), r2 = Math.max(0, e.top), o3 = Math.min(innerHeight, e.bottom), l9 = s45.ownerDocument.body;
  for (let h = s45.parentNode; h && h != l9; ) if (h.nodeType == 1) {
    let a2 = h, c3 = globalThis.getComputedStyle(a2);
    if ((a2.scrollHeight > a2.clientHeight || a2.scrollWidth > a2.clientWidth) && c3.overflow != "visible") {
      let f = a2.getBoundingClientRect();
      i2 = Math.max(i2, f.left), n11 = Math.min(n11, f.right), r2 = Math.max(r2, f.top), o3 = Math.min(o3, f.bottom);
    }
    h = c3.position == "absolute" || c3.position == "fixed" ? a2.offsetParent : a2.parentNode;
  } else if (h.nodeType == 11) h = h.host;
  else break;
  return {
    left: i2 - e.left,
    right: Math.max(i2, n11) - e.left,
    top: r2 - (e.top + t3),
    bottom: Math.max(r2, o3) - (e.top + t3)
  };
}
function Qn(s45, t3) {
  let e = s45.getBoundingClientRect();
  return {
    left: 0,
    right: e.right - e.left,
    top: t3,
    bottom: e.bottom - (e.top + t3)
  };
}
var kt = class {
  constructor(t3, e, i2) {
    this.from = t3, this.to = e, this.size = i2;
  }
  static same(t3, e) {
    if (t3.length != e.length) return false;
    for (let i2 = 0; i2 < t3.length; i2++) {
      let n11 = t3[i2], r2 = e[i2];
      if (n11.from != r2.from || n11.to != r2.to || n11.size != r2.size) return false;
    }
    return true;
  }
  draw(t3) {
    return C2.replace({
      widget: new Je2(this.size, t3)
    }).range(this.from, this.to);
  }
};
var Je2 = class extends K2 {
  constructor(t3, e) {
    super(), this.size = t3, this.vertical = e;
  }
  eq(t3) {
    return t3.size == this.size && t3.vertical == this.vertical;
  }
  toDOM() {
    let t3 = document.createElement("div");
    return this.vertical ? t3.style.height = this.size + "px" : (t3.style.width = this.size + "px", t3.style.height = "2px", t3.style.display = "inline-block"), t3;
  }
  get estimatedHeight() {
    return this.vertical ? this.size : -1;
  }
};
var ce2 = class {
  constructor(t3) {
    this.state = t3, this.pixelViewport = {
      left: 0,
      right: globalThis.innerWidth,
      top: 0,
      bottom: 0
    }, this.inView = true, this.paddingTop = 0, this.paddingBottom = 0, this.contentDOMWidth = 0, this.contentDOMHeight = 0, this.editorHeight = 0, this.editorWidth = 0, this.heightOracle = new le(), this.scaler = $i, this.scrollTarget = null, this.printing = false, this.mustMeasureContent = true, this.defaultTextDirection = O2.RTL, this.visibleRanges = [], this.mustEnforceCursorAssoc = false, this.stateDeco = t3.facet(Ht).filter((e) => typeof e != "function"), this.heightMap = W2.empty().applyChanges(this.stateDeco, m.empty, this.heightOracle.setDoc(t3.doc), [
      new it2(0, 0, 0, t3.doc.length)
    ]), this.viewport = this.getViewport(0, null), this.updateViewportLines(), this.updateForViewport(), this.lineGaps = this.ensureLineGaps([]), this.lineGapDeco = C2.set(this.lineGaps.map((e) => e.draw(false))), this.computeVisibleRanges();
  }
  updateForViewport() {
    let t3 = [
      this.viewport
    ], { main: e } = this.state.selection;
    for (let i2 = 0; i2 <= 1; i2++) {
      let n11 = i2 ? e.head : e.anchor;
      if (!t3.some(({ from: r2, to: o3 }) => n11 >= r2 && n11 <= o3)) {
        let { from: r2, to: o3 } = this.lineBlockAt(n11);
        t3.push(new at2(r2, o3));
      }
    }
    this.viewports = t3.sort((i2, n11) => i2.from - n11.from), this.scaler = this.heightMap.height <= 7e6 ? $i : new Ze2(this.heightOracle.doc, this.heightMap, this.viewports);
  }
  updateViewportLines() {
    this.viewportLines = [], this.heightMap.forEachLine(this.viewport.from, this.viewport.to, this.state.doc, 0, 0, (t3) => {
      this.viewportLines.push(this.scaler.scale == 1 ? t3 : wt(t3, this.scaler));
    });
  }
  update(t3, e = null) {
    this.state = t3.state;
    let i2 = this.stateDeco;
    this.stateDeco = this.state.facet(Ht).filter((a2) => typeof a2 != "function");
    let n11 = t3.changedRanges, r2 = it2.extendWithRanges(n11, Jn(i2, this.stateDeco, t3 ? t3.changes : P.empty(this.state.doc.length))), o3 = this.heightMap.height;
    this.heightMap = this.heightMap.applyChanges(this.stateDeco, t3.startState.doc, this.heightOracle.setDoc(this.state.doc), r2), this.heightMap.height != o3 && (t3.flags |= 2);
    let l9 = r2.length ? this.mapViewport(this.viewport, t3.changes) : this.viewport;
    (e && (e.range.head < l9.from || e.range.head > l9.to) || !this.viewportIsAppropriate(l9)) && (l9 = this.getViewport(0, e));
    let h = !t3.changes.empty || t3.flags & 2 || l9.from != this.viewport.from || l9.to != this.viewport.to;
    this.viewport = l9, this.updateForViewport(), h && this.updateViewportLines(), (this.lineGaps.length || this.viewport.to - this.viewport.from > 4e3) && this.updateLineGaps(this.ensureLineGaps(this.mapLineGaps(this.lineGaps, t3.changes))), t3.flags |= this.computeVisibleRanges(), e && (this.scrollTarget = e), !this.mustEnforceCursorAssoc && t3.selectionSet && t3.view.lineWrapping && t3.state.selection.main.empty && t3.state.selection.main.assoc && (this.mustEnforceCursorAssoc = true);
  }
  measure(t3) {
    let e = t3.contentDOM, i2 = globalThis.getComputedStyle(e), n11 = this.heightOracle, r2 = i2.whiteSpace;
    this.defaultTextDirection = i2.direction == "rtl" ? O2.RTL : O2.LTR;
    let o3 = this.heightOracle.mustRefreshForWrapping(r2), l9 = o3 || this.mustMeasureContent || this.contentDOMHeight != e.clientHeight;
    this.contentDOMHeight = e.clientHeight, this.mustMeasureContent = false;
    let h = 0, a2 = 0, c3 = parseInt(i2.paddingTop) || 0, f = parseInt(i2.paddingBottom) || 0;
    (this.paddingTop != c3 || this.paddingBottom != f) && (this.paddingTop = c3, this.paddingBottom = f, h |= 10), this.editorWidth != t3.scrollDOM.clientWidth && (n11.lineWrapping && (l9 = true), this.editorWidth = t3.scrollDOM.clientWidth, h |= 8);
    let u2 = (this.printing ? Qn : Zn)(e, this.paddingTop), d = u2.top - this.pixelViewport.top, p2 = u2.bottom - this.pixelViewport.bottom;
    this.pixelViewport = u2;
    let m4 = this.pixelViewport.bottom > this.pixelViewport.top && this.pixelViewport.right > this.pixelViewport.left;
    if (m4 != this.inView && (this.inView = m4, m4 && (l9 = true)), !this.inView) return 0;
    let b4 = e.clientWidth;
    if ((this.contentDOMWidth != b4 || this.editorHeight != t3.scrollDOM.clientHeight) && (this.contentDOMWidth = b4, this.editorHeight = t3.scrollDOM.clientHeight, h |= 8), l9) {
      let k4 = t3.docView.measureVisibleLineHeights(this.viewport);
      if (n11.mustRefreshForHeights(k4) && (o3 = true), o3 || n11.lineWrapping && Math.abs(b4 - this.contentDOMWidth) > n11.charWidth) {
        let { lineHeight: v3, charWidth: w5 } = t3.docView.measureTextSize();
        o3 = n11.refresh(r2, v3, w5, b4 / w5, k4), o3 && (t3.docView.minWidth = 0, h |= 8);
      }
      d > 0 && p2 > 0 ? a2 = Math.max(d, p2) : d < 0 && p2 < 0 && (a2 = Math.min(d, p2)), n11.heightChanged = false;
      for (let v3 of this.viewports) {
        let w5 = v3.from == this.viewport.from ? k4 : t3.docView.measureVisibleLineHeights(v3);
        this.heightMap = this.heightMap.updateHeight(n11, 0, o3, new he2(v3.from, w5));
      }
      n11.heightChanged && (h |= 2);
    }
    let y4 = !this.viewportIsAppropriate(this.viewport, a2) || this.scrollTarget && (this.scrollTarget.range.head < this.viewport.from || this.scrollTarget.range.head > this.viewport.to);
    return y4 && (this.viewport = this.getViewport(a2, this.scrollTarget)), this.updateForViewport(), (h & 2 || y4) && this.updateViewportLines(), (this.lineGaps.length || this.viewport.to - this.viewport.from > 4e3) && this.updateLineGaps(this.ensureLineGaps(o3 ? [] : this.lineGaps)), h |= this.computeVisibleRanges(), this.mustEnforceCursorAssoc && (this.mustEnforceCursorAssoc = false, t3.docView.enforceCursorAssoc()), h;
  }
  get visibleTop() {
    return this.scaler.fromDOM(this.pixelViewport.top);
  }
  get visibleBottom() {
    return this.scaler.fromDOM(this.pixelViewport.bottom);
  }
  getViewport(t3, e) {
    let i2 = 0.5 - Math.max(-0.5, Math.min(0.5, t3 / 1e3 / 2)), n11 = this.heightMap, r2 = this.state.doc, { visibleTop: o3, visibleBottom: l9 } = this, h = new at2(n11.lineAt(o3 - i2 * 1e3, A.ByHeight, r2, 0, 0).from, n11.lineAt(l9 + (1 - i2) * 1e3, A.ByHeight, r2, 0, 0).to);
    if (e) {
      let { head: a2 } = e.range;
      if (a2 < h.from || a2 > h.to) {
        let c3 = Math.min(this.editorHeight, this.pixelViewport.bottom - this.pixelViewport.top), f = n11.lineAt(a2, A.ByPos, r2, 0, 0), u2;
        e.y == "center" ? u2 = (f.top + f.bottom) / 2 - c3 / 2 : e.y == "start" || e.y == "nearest" && a2 < h.from ? u2 = f.top : u2 = f.bottom - c3, h = new at2(n11.lineAt(u2 - 1e3 / 2, A.ByHeight, r2, 0, 0).from, n11.lineAt(u2 + c3 + 1e3 / 2, A.ByHeight, r2, 0, 0).to);
      }
    }
    return h;
  }
  mapViewport(t3, e) {
    let i2 = e.mapPos(t3.from, -1), n11 = e.mapPos(t3.to, 1);
    return new at2(this.heightMap.lineAt(i2, A.ByPos, this.state.doc, 0, 0).from, this.heightMap.lineAt(n11, A.ByPos, this.state.doc, 0, 0).to);
  }
  viewportIsAppropriate({ from: t3, to: e }, i2 = 0) {
    if (!this.inView) return true;
    let { top: n11 } = this.heightMap.lineAt(t3, A.ByPos, this.state.doc, 0, 0), { bottom: r2 } = this.heightMap.lineAt(e, A.ByPos, this.state.doc, 0, 0), { visibleTop: o3, visibleBottom: l9 } = this;
    return (t3 == 0 || n11 <= o3 - Math.max(10, Math.min(-i2, 250))) && (e == this.state.doc.length || r2 >= l9 + Math.max(10, Math.min(i2, 250))) && n11 > o3 - 2 * 1e3 && r2 < l9 + 2 * 1e3;
  }
  mapLineGaps(t3, e) {
    if (!t3.length || e.empty) return t3;
    let i2 = [];
    for (let n11 of t3) e.touchesRange(n11.from, n11.to) || i2.push(new kt(e.mapPos(n11.from), e.mapPos(n11.to), n11.size));
    return i2;
  }
  ensureLineGaps(t3) {
    let e = [];
    if (this.defaultTextDirection != O2.LTR) return e;
    for (let i2 of this.viewportLines) {
      if (i2.length < 4e3) continue;
      let n11 = tr(i2.from, i2.to, this.stateDeco);
      if (n11.total < 4e3) continue;
      let r2, o3;
      if (this.heightOracle.lineWrapping) {
        let a2 = 2e3 / this.heightOracle.lineLength * this.heightOracle.lineHeight;
        r2 = qt(n11, (this.visibleTop - i2.top - a2) / i2.height), o3 = qt(n11, (this.visibleBottom - i2.top + a2) / i2.height);
      } else {
        let a2 = n11.total * this.heightOracle.charWidth, c3 = 2e3 * this.heightOracle.charWidth;
        r2 = qt(n11, (this.pixelViewport.left - c3) / a2), o3 = qt(n11, (this.pixelViewport.right + c3) / a2);
      }
      let l9 = [];
      r2 > i2.from && l9.push({
        from: i2.from,
        to: r2
      }), o3 < i2.to && l9.push({
        from: o3,
        to: i2.to
      });
      let h = this.state.selection.main;
      h.from >= i2.from && h.from <= i2.to && Gi(l9, h.from - 10, h.from + 10), !h.empty && h.to >= i2.from && h.to <= i2.to && Gi(l9, h.to - 10, h.to + 10);
      for (let { from: a2, to: c3 } of l9) c3 - a2 > 1e3 && e.push(er(t3, (f) => f.from >= i2.from && f.to <= i2.to && Math.abs(f.from - a2) < 1e3 && Math.abs(f.to - c3) < 1e3) || new kt(a2, c3, this.gapSize(i2, a2, c3, n11)));
    }
    return e;
  }
  gapSize(t3, e, i2, n11) {
    let r2 = ji(n11, i2) - ji(n11, e);
    return this.heightOracle.lineWrapping ? t3.height * r2 : n11.total * this.heightOracle.charWidth * r2;
  }
  updateLineGaps(t3) {
    kt.same(t3, this.lineGaps) || (this.lineGaps = t3, this.lineGapDeco = C2.set(t3.map((e) => e.draw(this.heightOracle.lineWrapping))));
  }
  computeVisibleRanges() {
    let t3 = this.stateDeco;
    this.lineGaps.length && (t3 = t3.concat(this.lineGapDeco));
    let e = [];
    O.spans(t3, this.viewport.from, this.viewport.to, {
      span(n11, r2) {
        e.push({
          from: n11,
          to: r2
        });
      },
      point() {
      }
    }, 20);
    let i2 = e.length != this.visibleRanges.length || this.visibleRanges.some((n11, r2) => n11.from != e[r2].from || n11.to != e[r2].to);
    return this.visibleRanges = e, i2 ? 4 : 0;
  }
  lineBlockAt(t3) {
    return t3 >= this.viewport.from && t3 <= this.viewport.to && this.viewportLines.find((e) => e.from <= t3 && e.to >= t3) || wt(this.heightMap.lineAt(t3, A.ByPos, this.state.doc, 0, 0), this.scaler);
  }
  lineBlockAtHeight(t3) {
    return wt(this.heightMap.lineAt(this.scaler.fromDOM(t3), A.ByHeight, this.state.doc, 0, 0), this.scaler);
  }
  elementAtHeight(t3) {
    return wt(this.heightMap.blockAt(this.scaler.fromDOM(t3), this.state.doc, 0, 0), this.scaler);
  }
  get docHeight() {
    return this.scaler.toDOM(this.heightMap.height);
  }
  get contentHeight() {
    return this.docHeight + this.paddingTop + this.paddingBottom;
  }
};
var at2 = class {
  constructor(t3, e) {
    this.from = t3, this.to = e;
  }
};
function tr(s45, t3, e) {
  let i2 = [], n11 = s45, r2 = 0;
  return O.spans(e, s45, t3, {
    span() {
    },
    point(o3, l9) {
      o3 > n11 && (i2.push({
        from: n11,
        to: o3
      }), r2 += o3 - n11), n11 = l9;
    }
  }, 20), n11 < t3 && (i2.push({
    from: n11,
    to: t3
  }), r2 += t3 - n11), {
    total: r2,
    ranges: i2
  };
}
function qt({ total: s45, ranges: t3 }, e) {
  if (e <= 0) return t3[0].from;
  if (e >= 1) return t3[t3.length - 1].to;
  let i2 = Math.floor(s45 * e);
  for (let n11 = 0; ; n11++) {
    let { from: r2, to: o3 } = t3[n11], l9 = o3 - r2;
    if (i2 <= l9) return r2 + i2;
    i2 -= l9;
  }
}
function ji(s45, t3) {
  let e = 0;
  for (let { from: i2, to: n11 } of s45.ranges) {
    if (t3 <= n11) {
      e += t3 - i2;
      break;
    }
    e += n11 - i2;
  }
  return e / s45.total;
}
function Gi(s45, t3, e) {
  for (let i2 = 0; i2 < s45.length; i2++) {
    let n11 = s45[i2];
    if (n11.from < e && n11.to > t3) {
      let r2 = [];
      n11.from < t3 && r2.push({
        from: n11.from,
        to: t3
      }), n11.to > e && r2.push({
        from: e,
        to: n11.to
      }), s45.splice(i2, 1, ...r2), i2 += r2.length - 1;
    }
  }
}
function er(s45, t3) {
  for (let e of s45) if (t3(e)) return e;
}
var $i = {
  toDOM(s45) {
    return s45;
  },
  fromDOM(s45) {
    return s45;
  },
  scale: 1
};
var Ze2 = class {
  constructor(t3, e, i2) {
    let n11 = 0, r2 = 0, o3 = 0;
    this.viewports = i2.map(({ from: l9, to: h }) => {
      let a2 = e.lineAt(l9, A.ByPos, t3, 0, 0).top, c3 = e.lineAt(h, A.ByPos, t3, 0, 0).bottom;
      return n11 += c3 - a2, {
        from: l9,
        to: h,
        top: a2,
        bottom: c3,
        domTop: 0,
        domBottom: 0
      };
    }), this.scale = (7e6 - n11) / (e.height - n11);
    for (let l9 of this.viewports) l9.domTop = o3 + (l9.top - r2) * this.scale, o3 = l9.domBottom = l9.domTop + (l9.bottom - l9.top), r2 = l9.bottom;
  }
  toDOM(t3) {
    for (let e = 0, i2 = 0, n11 = 0; ; e++) {
      let r2 = e < this.viewports.length ? this.viewports[e] : null;
      if (!r2 || t3 < r2.top) return n11 + (t3 - i2) * this.scale;
      if (t3 <= r2.bottom) return r2.domTop + (t3 - r2.top);
      i2 = r2.bottom, n11 = r2.domBottom;
    }
  }
  fromDOM(t3) {
    for (let e = 0, i2 = 0, n11 = 0; ; e++) {
      let r2 = e < this.viewports.length ? this.viewports[e] : null;
      if (!r2 || t3 < r2.domTop) return i2 + (t3 - n11) / this.scale;
      if (t3 <= r2.domBottom) return r2.top + (t3 - r2.domTop);
      i2 = r2.bottom, n11 = r2.domBottom;
    }
  }
};
function wt(s45, t3) {
  if (t3.scale == 1) return s45;
  let e = t3.toDOM(s45.top), i2 = t3.toDOM(s45.bottom);
  return new J2(s45.from, s45.length, e, i2 - e, Array.isArray(s45.type) ? s45.type.map((n11) => wt(n11, t3)) : s45.type);
}
var Kt = y.define({
  combine: (s45) => s45.join(" ")
});
var Qe2 = y.define({
  combine: (s45) => s45.indexOf(true) > -1
});
var ti = T2.newName();
var Us = T2.newName();
var Xs = T2.newName();
var Js = {
  "&light": "." + Us,
  "&dark": "." + Xs
};
function ei(s45, t3, e) {
  return new T2(t3, {
    finish(i2) {
      return /&/.test(i2) ? i2.replace(/&\w*/, (n11) => {
        if (n11 == "&") return s45;
        if (!e || !e[n11]) throw new RangeError(`Unsupported selector: ${n11}`);
        return e[n11];
      }) : s45 + " " + i2;
    }
  });
}
var ir = ei("." + ti, {
  "&.cm-editor": {
    position: "relative !important",
    boxSizing: "border-box",
    "&.cm-focused": {
      outline: "1px dotted #212121"
    },
    display: "flex !important",
    flexDirection: "column"
  },
  ".cm-scroller": {
    display: "flex !important",
    alignItems: "flex-start !important",
    fontFamily: "monospace",
    lineHeight: 1.4,
    height: "100%",
    overflowX: "auto",
    position: "relative",
    zIndex: 0
  },
  ".cm-content": {
    margin: 0,
    flexGrow: 2,
    minHeight: "100%",
    display: "block",
    whiteSpace: "pre",
    wordWrap: "normal",
    boxSizing: "border-box",
    padding: "4px 0",
    outline: "none",
    "&[contenteditable=true]": {
      WebkitUserModify: "read-write-plaintext-only"
    }
  },
  ".cm-lineWrapping": {
    whiteSpace_fallback: "pre-wrap",
    whiteSpace: "break-spaces",
    wordBreak: "break-word",
    overflowWrap: "anywhere"
  },
  "&light .cm-content": {
    caretColor: "black"
  },
  "&dark .cm-content": {
    caretColor: "white"
  },
  ".cm-line": {
    display: "block",
    padding: "0 2px 0 4px"
  },
  ".cm-selectionLayer": {
    zIndex: -1,
    contain: "size style"
  },
  ".cm-selectionBackground": {
    position: "absolute"
  },
  "&light .cm-selectionBackground": {
    background: "#d9d9d9"
  },
  "&dark .cm-selectionBackground": {
    background: "#222"
  },
  "&light.cm-focused .cm-selectionBackground": {
    background: "#d7d4f0"
  },
  "&dark.cm-focused .cm-selectionBackground": {
    background: "#233"
  },
  ".cm-cursorLayer": {
    zIndex: 100,
    contain: "size style",
    pointerEvents: "none"
  },
  "&.cm-focused .cm-cursorLayer": {
    animation: "steps(1) cm-blink 1.2s infinite"
  },
  "@keyframes cm-blink": {
    "0%": {},
    "50%": {
      visibility: "hidden"
    },
    "100%": {}
  },
  "@keyframes cm-blink2": {
    "0%": {},
    "50%": {
      visibility: "hidden"
    },
    "100%": {}
  },
  ".cm-cursor, .cm-dropCursor": {
    position: "absolute",
    borderLeft: "1.2px solid black",
    marginLeft: "-0.6px",
    pointerEvents: "none"
  },
  ".cm-cursor": {
    display: "none"
  },
  "&dark .cm-cursor": {
    borderLeftColor: "#444"
  },
  "&.cm-focused .cm-cursor": {
    display: "block"
  },
  "&light .cm-activeLine": {
    backgroundColor: "#f3f9ff"
  },
  "&dark .cm-activeLine": {
    backgroundColor: "#223039"
  },
  "&light .cm-specialChar": {
    color: "red"
  },
  "&dark .cm-specialChar": {
    color: "#f78"
  },
  ".cm-gutters": {
    display: "flex",
    height: "100%",
    boxSizing: "border-box",
    left: 0,
    zIndex: 200
  },
  "&light .cm-gutters": {
    backgroundColor: "#f5f5f5",
    color: "#6c6c6c",
    borderRight: "1px solid #ddd"
  },
  "&dark .cm-gutters": {
    backgroundColor: "#333338",
    color: "#ccc"
  },
  ".cm-gutter": {
    display: "flex !important",
    flexDirection: "column",
    flexShrink: 0,
    boxSizing: "border-box",
    minHeight: "100%",
    overflow: "hidden"
  },
  ".cm-gutterElement": {
    boxSizing: "border-box"
  },
  ".cm-lineNumbers .cm-gutterElement": {
    padding: "0 3px 0 5px",
    minWidth: "20px",
    textAlign: "right",
    whiteSpace: "nowrap"
  },
  "&light .cm-activeLineGutter": {
    backgroundColor: "#e2f2ff"
  },
  "&dark .cm-activeLineGutter": {
    backgroundColor: "#222227"
  },
  ".cm-panels": {
    boxSizing: "border-box",
    position: "sticky",
    left: 0,
    right: 0
  },
  "&light .cm-panels": {
    backgroundColor: "#f5f5f5",
    color: "black"
  },
  "&light .cm-panels-top": {
    borderBottom: "1px solid #ddd"
  },
  "&light .cm-panels-bottom": {
    borderTop: "1px solid #ddd"
  },
  "&dark .cm-panels": {
    backgroundColor: "#333338",
    color: "white"
  },
  ".cm-tab": {
    display: "inline-block",
    overflow: "hidden",
    verticalAlign: "bottom"
  },
  ".cm-widgetBuffer": {
    verticalAlign: "text-top",
    height: "1em",
    display: "inline"
  },
  ".cm-placeholder": {
    color: "#888",
    display: "inline-block",
    verticalAlign: "top"
  },
  ".cm-button": {
    verticalAlign: "middle",
    color: "inherit",
    fontSize: "70%",
    padding: ".2em 1em",
    borderRadius: "1px"
  },
  "&light .cm-button": {
    backgroundImage: "linear-gradient(#eff1f5, #d9d9df)",
    border: "1px solid #888",
    "&:active": {
      backgroundImage: "linear-gradient(#b4b4b4, #d0d3d6)"
    }
  },
  "&dark .cm-button": {
    backgroundImage: "linear-gradient(#393939, #111)",
    border: "1px solid #888",
    "&:active": {
      backgroundImage: "linear-gradient(#111, #333)"
    }
  },
  ".cm-textfield": {
    verticalAlign: "middle",
    color: "inherit",
    fontSize: "70%",
    border: "1px solid silver",
    padding: ".2em .5em"
  },
  "&light .cm-textfield": {
    backgroundColor: "white"
  },
  "&dark .cm-textfield": {
    border: "1px solid #555",
    backgroundColor: "inherit"
  }
}, Js);
var sr = {
  childList: true,
  characterData: true,
  subtree: true,
  attributes: true,
  characterDataOldValue: true
};
var xe2 = g2.ie && g2.ie_version <= 11;
var ii = class {
  constructor(t3, e, i2) {
    this.view = t3, this.onChange = e, this.onScrollChanged = i2, this.active = false, this.selectionRange = new Oe2(), this.selectionChanged = false, this.delayedFlush = -1, this.resizeTimeout = -1, this.queue = [], this.delayedAndroidKey = null, this.scrollTargets = [], this.intersection = null, this.resize = null, this.intersecting = false, this.gapIntersection = null, this.gaps = [], this.parentCheck = -1, this.dom = t3.contentDOM, this.observer = new MutationObserver((n11) => {
      for (let r2 of n11) this.queue.push(r2);
      (g2.ie && g2.ie_version <= 11 || g2.ios && t3.composing) && n11.some((r2) => r2.type == "childList" && r2.removedNodes.length || r2.type == "characterData" && r2.oldValue.length > r2.target.nodeValue.length) ? this.flushSoon() : this.flush();
    }), xe2 && (this.onCharData = (n11) => {
      this.queue.push({
        target: n11.target,
        type: "characterData",
        oldValue: n11.prevValue
      }), this.flushSoon();
    }), this.onSelectionChange = this.onSelectionChange.bind(this), globalThis.addEventListener("resize", this.onResize = this.onResize.bind(this)), typeof ResizeObserver == "function" && (this.resize = new ResizeObserver(() => {
      this.view.docView.lastUpdate < Date.now() - 75 && this.onResize();
    }), this.resize.observe(t3.scrollDOM)), globalThis.addEventListener("beforeprint", this.onPrint = this.onPrint.bind(this)), this.start(), globalThis.addEventListener("scroll", this.onScroll = this.onScroll.bind(this)), typeof IntersectionObserver == "function" && (this.intersection = new IntersectionObserver((n11) => {
      this.parentCheck < 0 && (this.parentCheck = setTimeout(this.listenForScroll.bind(this), 1e3)), n11.length > 0 && n11[n11.length - 1].intersectionRatio > 0 != this.intersecting && (this.intersecting = !this.intersecting, this.intersecting != this.view.inView && this.onScrollChanged(document.createEvent("Event")));
    }, {}), this.intersection.observe(this.dom), this.gapIntersection = new IntersectionObserver((n11) => {
      n11.length > 0 && n11[n11.length - 1].intersectionRatio > 0 && this.onScrollChanged(document.createEvent("Event"));
    }, {})), this.listenForScroll(), this.readSelectionRange(), this.dom.ownerDocument.addEventListener("selectionchange", this.onSelectionChange);
  }
  onScroll(t3) {
    this.intersecting && this.flush(false), this.onScrollChanged(t3);
  }
  onResize() {
    this.resizeTimeout < 0 && (this.resizeTimeout = setTimeout(() => {
      this.resizeTimeout = -1, this.view.requestMeasure();
    }, 50));
  }
  onPrint() {
    this.view.viewState.printing = true, this.view.measure(), setTimeout(() => {
      this.view.viewState.printing = false, this.view.requestMeasure();
    }, 500);
  }
  updateGaps(t3) {
    if (this.gapIntersection && (t3.length != this.gaps.length || this.gaps.some((e, i2) => e != t3[i2]))) {
      this.gapIntersection.disconnect();
      for (let e of t3) this.gapIntersection.observe(e);
      this.gaps = t3;
    }
  }
  onSelectionChange(t3) {
    if (!this.readSelectionRange() || this.delayedAndroidKey) return;
    let { view: e } = this, i2 = this.selectionRange;
    if (e.state.facet(Nt) ? e.root.activeElement != this.dom : !De2(e.dom, i2)) return;
    let n11 = i2.anchorNode && e.docView.nearest(i2.anchorNode);
    n11 && n11.ignoreEvent(t3) || ((g2.ie && g2.ie_version <= 11 || g2.android && g2.chrome) && !e.state.selection.main.empty && i2.focusNode && Ut(i2.focusNode, i2.focusOffset, i2.anchorNode, i2.anchorOffset) ? this.flushSoon() : this.flush(false));
  }
  readSelectionRange() {
    let { root: t3 } = this.view, e = Yt(t3), i2 = g2.safari && t3.nodeType == 11 && gn() == this.view.contentDOM && nr(this.view) || e;
    return this.selectionRange.eq(i2) ? false : (this.selectionRange.setRange(i2), this.selectionChanged = true);
  }
  setSelectionRange(t3, e) {
    this.selectionRange.set(t3.node, t3.offset, e.node, e.offset), this.selectionChanged = false;
  }
  clearSelectionRange() {
    this.selectionRange.set(null, 0, null, 0);
  }
  listenForScroll() {
    this.parentCheck = -1;
    let t3 = 0, e = null;
    for (let i2 = this.dom; i2; ) if (i2.nodeType == 1) !e && t3 < this.scrollTargets.length && this.scrollTargets[t3] == i2 ? t3++ : e || (e = this.scrollTargets.slice(0, t3)), e && e.push(i2), i2 = i2.assignedSlot || i2.parentNode;
    else if (i2.nodeType == 11) i2 = i2.host;
    else break;
    if (t3 < this.scrollTargets.length && !e && (e = this.scrollTargets.slice(0, t3)), e) {
      for (let i2 of this.scrollTargets) i2.removeEventListener("scroll", this.onScroll);
      for (let i2 of this.scrollTargets = e) i2.addEventListener("scroll", this.onScroll);
    }
  }
  ignore(t3) {
    if (!this.active) return t3();
    try {
      return this.stop(), t3();
    } finally {
      this.start(), this.clear();
    }
  }
  start() {
    this.active || (this.observer.observe(this.dom, sr), xe2 && this.dom.addEventListener("DOMCharacterDataModified", this.onCharData), this.active = true);
  }
  stop() {
    this.active && (this.active = false, this.observer.disconnect(), xe2 && this.dom.removeEventListener("DOMCharacterDataModified", this.onCharData));
  }
  clear() {
    this.processRecords(), this.queue.length = 0, this.selectionChanged = false;
  }
  delayAndroidKey(t3, e) {
    this.delayedAndroidKey || requestAnimationFrame(() => {
      let i2 = this.delayedAndroidKey;
      this.delayedAndroidKey = null, this.delayedFlush = -1, this.flush() || Ct(this.view.contentDOM, i2.key, i2.keyCode);
    }), (!this.delayedAndroidKey || t3 == "Enter") && (this.delayedAndroidKey = {
      key: t3,
      keyCode: e
    });
  }
  flushSoon() {
    this.delayedFlush < 0 && (this.delayedFlush = globalThis.setTimeout(() => {
      this.delayedFlush = -1, this.flush();
    }, 20));
  }
  forceFlush() {
    this.delayedFlush >= 0 && (globalThis.clearTimeout(this.delayedFlush), this.delayedFlush = -1, this.flush());
  }
  processRecords() {
    let t3 = this.queue;
    for (let r2 of this.observer.takeRecords()) t3.push(r2);
    t3.length && (this.queue = []);
    let e = -1, i2 = -1, n11 = false;
    for (let r2 of t3) {
      let o3 = this.readMutation(r2);
      o3 && (o3.typeOver && (n11 = true), e == -1 ? { from: e, to: i2 } = o3 : (e = Math.min(o3.from, e), i2 = Math.max(o3.to, i2)));
    }
    return {
      from: e,
      to: i2,
      typeOver: n11
    };
  }
  flush(t3 = true) {
    if (this.delayedFlush >= 0 || this.delayedAndroidKey) return;
    t3 && this.readSelectionRange();
    let { from: e, to: i2, typeOver: n11 } = this.processRecords(), r2 = this.selectionChanged && De2(this.dom, this.selectionRange);
    if (e < 0 && !r2) return;
    this.selectionChanged = false;
    let o3 = this.view.state, l9 = this.onChange(e, i2, n11);
    return this.view.state == o3 && this.view.update([]), l9;
  }
  readMutation(t3) {
    let e = this.view.docView.nearest(t3.target);
    if (!e || e.ignoreMutation(t3)) return null;
    if (e.markDirty(t3.type == "attributes"), t3.type == "attributes" && (e.dirty |= 4), t3.type == "childList") {
      let i2 = _i(e, t3.previousSibling || t3.target.previousSibling, -1), n11 = _i(e, t3.nextSibling || t3.target.nextSibling, 1);
      return {
        from: i2 ? e.posAfter(i2) : e.posAtStart,
        to: n11 ? e.posBefore(n11) : e.posAtEnd,
        typeOver: false
      };
    } else return t3.type == "characterData" ? {
      from: e.posAtStart,
      to: e.posAtEnd,
      typeOver: t3.target.nodeValue == t3.oldValue
    } : null;
  }
  destroy() {
    var t3, e, i2;
    this.stop(), (t3 = this.intersection) === null || t3 === void 0 || t3.disconnect(), (e = this.gapIntersection) === null || e === void 0 || e.disconnect(), (i2 = this.resize) === null || i2 === void 0 || i2.disconnect();
    for (let n11 of this.scrollTargets) n11.removeEventListener("scroll", this.onScroll);
    globalThis.removeEventListener("scroll", this.onScroll), globalThis.removeEventListener("resize", this.onResize), globalThis.removeEventListener("beforeprint", this.onPrint), this.dom.ownerDocument.removeEventListener("selectionchange", this.onSelectionChange), clearTimeout(this.parentCheck), clearTimeout(this.resizeTimeout);
  }
};
function _i(s45, t3, e) {
  for (; t3; ) {
    let i2 = R2.get(t3);
    if (i2 && i2.parent == s45) return i2;
    let n11 = t3.parentNode;
    t3 = n11 != s45.dom ? n11 : e > 0 ? t3.nextSibling : t3.previousSibling;
  }
  return null;
}
function nr(s45) {
  let t3 = null;
  function e(h) {
    h.preventDefault(), h.stopImmediatePropagation(), t3 = h.getTargetRanges()[0];
  }
  if (s45.contentDOM.addEventListener("beforeinput", e, true), document.execCommand("indent"), s45.contentDOM.removeEventListener("beforeinput", e, true), !t3) return null;
  let i2 = t3.startContainer, n11 = t3.startOffset, r2 = t3.endContainer, o3 = t3.endOffset, l9 = s45.docView.domAtPos(s45.state.selection.main.anchor);
  return Ut(l9.node, l9.offset, r2, o3) && ([i2, n11, r2, o3] = [
    r2,
    o3,
    i2,
    n11
  ]), {
    anchorNode: i2,
    anchorOffset: n11,
    focusNode: r2,
    focusOffset: o3
  };
}
function rr(s45, t3, e, i2) {
  let n11, r2, o3 = s45.state.selection.main;
  if (t3 > -1) {
    let l9 = s45.docView.domBoundsAround(t3, e, 0);
    if (!l9 || s45.state.readOnly) return false;
    let { from: h, to: a2 } = l9, c3 = s45.docView.impreciseHead || s45.docView.impreciseAnchor ? [] : lr(s45), f = new se2(c3, s45.state);
    f.readRange(l9.startDOM, l9.endDOM);
    let u2 = o3.from, d = null;
    (s45.inputState.lastKeyCode === 8 && s45.inputState.lastKeyTime > Date.now() - 100 || g2.android && f.text.length < a2 - h) && (u2 = o3.to, d = "end");
    let p2 = or(s45.state.doc.sliceString(h, a2, X2), f.text, u2 - h, d);
    p2 && (g2.chrome && s45.inputState.lastKeyCode == 13 && p2.toB == p2.from + 2 && f.text.slice(p2.from, p2.toB) == X2 + X2 && p2.toB--, n11 = {
      from: h + p2.from,
      to: h + p2.toA,
      insert: m.of(f.text.slice(p2.from, p2.toB).split(X2))
    }), r2 = hr(c3, h);
  } else if (s45.hasFocus || !s45.state.facet(Nt)) {
    let l9 = s45.observer.selectionRange, { impreciseHead: h, impreciseAnchor: a2 } = s45.docView, c3 = h && h.node == l9.focusNode && h.offset == l9.focusOffset || !pt(s45.contentDOM, l9.focusNode) ? s45.state.selection.main.head : s45.docView.posFromDOM(l9.focusNode, l9.focusOffset), f = a2 && a2.node == l9.anchorNode && a2.offset == l9.anchorOffset || !pt(s45.contentDOM, l9.anchorNode) ? s45.state.selection.main.anchor : s45.docView.posFromDOM(l9.anchorNode, l9.anchorOffset);
    (c3 != o3.head || f != o3.anchor) && (r2 = x.single(f, c3));
  }
  if (!n11 && !r2) return false;
  if (!n11 && i2 && !o3.empty && r2 && r2.main.empty ? n11 = {
    from: o3.from,
    to: o3.to,
    insert: s45.state.doc.slice(o3.from, o3.to)
  } : n11 && n11.from >= o3.from && n11.to <= o3.to && (n11.from != o3.from || n11.to != o3.to) && o3.to - o3.from - (n11.to - n11.from) <= 4 ? n11 = {
    from: o3.from,
    to: o3.to,
    insert: s45.state.doc.slice(o3.from, n11.from).append(n11.insert).append(s45.state.doc.slice(n11.to, o3.to))
  } : (g2.mac || g2.android) && n11 && n11.from == n11.to && n11.from == o3.head - 1 && n11.insert.toString() == "." && (n11 = {
    from: o3.from,
    to: o3.to,
    insert: m.of([
      " "
    ])
  }), n11) {
    let l9 = s45.state;
    if (g2.ios && s45.inputState.flushIOSKey(s45) || g2.android && (n11.from == o3.from && n11.to == o3.to && n11.insert.length == 1 && n11.insert.lines == 2 && Ct(s45.contentDOM, "Enter", 13) || n11.from == o3.from - 1 && n11.to == o3.to && n11.insert.length == 0 && Ct(s45.contentDOM, "Backspace", 8) || n11.from == o3.from && n11.to == o3.to + 1 && n11.insert.length == 0 && Ct(s45.contentDOM, "Delete", 46))) return true;
    let h = n11.insert.toString();
    if (s45.state.facet(Ts).some((f) => f(s45, n11.from, n11.to, h))) return true;
    s45.inputState.composing >= 0 && s45.inputState.composing++;
    let a2;
    if (n11.from >= o3.from && n11.to <= o3.to && n11.to - n11.from >= (o3.to - o3.from) / 3 && (!r2 || r2.main.empty && r2.main.from == n11.from + n11.insert.length) && s45.inputState.composing < 0) {
      let f = o3.from < n11.from ? l9.sliceDoc(o3.from, n11.from) : "", u2 = o3.to > n11.to ? l9.sliceDoc(n11.to, o3.to) : "";
      a2 = l9.replaceSelection(s45.state.toText(f + n11.insert.sliceString(0, void 0, s45.state.lineBreak) + u2));
    } else {
      let f = l9.changes(n11), u2 = r2 && !l9.selection.main.eq(r2.main) && r2.main.to <= f.newLength ? r2.main : void 0;
      if (l9.selection.ranges.length > 1 && s45.inputState.composing >= 0 && n11.to <= o3.to && n11.to >= o3.to - 10) {
        let d = s45.state.sliceDoc(n11.from, n11.to), p2 = Ws(s45) || s45.state.doc.lineAt(o3.head), m4 = o3.to - n11.to, b4 = o3.to - o3.from;
        a2 = l9.changeByRange((y4) => {
          if (y4.from == o3.from && y4.to == o3.to) return {
            changes: f,
            range: u2 || y4.map(f)
          };
          let k4 = y4.to - m4, v3 = k4 - d.length;
          if (y4.to - y4.from != b4 || s45.state.sliceDoc(v3, k4) != d || p2 && y4.to >= p2.from && y4.from <= p2.to) return {
            range: y4
          };
          let w5 = l9.changes({
            from: v3,
            to: k4,
            insert: n11.insert
          }), L5 = y4.to - o3.to;
          return {
            changes: w5,
            range: u2 ? x.range(Math.max(0, u2.anchor + L5), Math.max(0, u2.head + L5)) : y4.map(w5)
          };
        });
      } else a2 = {
        changes: f,
        selection: u2 && l9.selection.replaceRange(u2)
      };
    }
    let c3 = "input.type";
    return s45.composing && (c3 += ".compose", s45.inputState.compositionFirstChange && (c3 += ".start", s45.inputState.compositionFirstChange = false)), s45.dispatch(a2, {
      scrollIntoView: true,
      userEvent: c3
    }), true;
  } else if (r2 && !r2.main.eq(o3)) {
    let l9 = false, h = "select";
    return s45.inputState.lastSelectionTime > Date.now() - 50 && (s45.inputState.lastSelectionOrigin == "select" && (l9 = true), h = s45.inputState.lastSelectionOrigin), s45.dispatch({
      selection: r2,
      scrollIntoView: l9,
      userEvent: h
    }), true;
  } else return false;
}
function or(s45, t3, e, i2) {
  let n11 = Math.min(s45.length, t3.length), r2 = 0;
  for (; r2 < n11 && s45.charCodeAt(r2) == t3.charCodeAt(r2); ) r2++;
  if (r2 == n11 && s45.length == t3.length) return null;
  let o3 = s45.length, l9 = t3.length;
  for (; o3 > 0 && l9 > 0 && s45.charCodeAt(o3 - 1) == t3.charCodeAt(l9 - 1); ) o3--, l9--;
  if (i2 == "end") {
    let h = Math.max(0, r2 - Math.min(o3, l9));
    e -= o3 + h - r2;
  }
  if (o3 < r2 && s45.length < t3.length) {
    let h = e <= r2 && e >= o3 ? r2 - e : 0;
    r2 -= h, l9 = r2 + (l9 - o3), o3 = r2;
  } else if (l9 < r2) {
    let h = e <= r2 && e >= l9 ? r2 - e : 0;
    r2 -= h, o3 = r2 + (o3 - l9), l9 = r2;
  }
  return {
    from: r2,
    toA: o3,
    toB: l9
  };
}
function lr(s45) {
  let t3 = [];
  if (s45.root.activeElement != s45.contentDOM) return t3;
  let { anchorNode: e, anchorOffset: i2, focusNode: n11, focusOffset: r2 } = s45.observer.selectionRange;
  return e && (t3.push(new ne2(e, i2)), (n11 != e || r2 != i2) && t3.push(new ne2(n11, r2))), t3;
}
function hr(s45, t3) {
  if (s45.length == 0) return null;
  let e = s45[0].pos, i2 = s45.length == 2 ? s45[1].pos : e;
  return e > -1 && i2 > -1 ? x.single(e + t3, i2 + t3) : null;
}
var M2 = class s41 {
  constructor(t3 = {}) {
    this.plugins = [], this.pluginMap = /* @__PURE__ */ new Map(), this.editorAttrs = {}, this.contentAttrs = {}, this.bidiCache = [], this.destroyed = false, this.updateState = 2, this.measureScheduled = -1, this.measureRequests = [], this.contentDOM = document.createElement("div"), this.scrollDOM = document.createElement("div"), this.scrollDOM.tabIndex = -1, this.scrollDOM.className = "cm-scroller", this.scrollDOM.appendChild(this.contentDOM), this.announceDOM = document.createElement("div"), this.announceDOM.style.cssText = "position: absolute; top: -10000px", this.announceDOM.setAttribute("aria-live", "polite"), this.dom = document.createElement("div"), this.dom.appendChild(this.announceDOM), this.dom.appendChild(this.scrollDOM), this._dispatch = t3.dispatch || ((e) => this.update([
      e
    ])), this.dispatch = this.dispatch.bind(this), this.root = t3.root || wn(t3.parent) || document, this.viewState = new ce2(t3.state || I.create()), this.plugins = this.state.facet(bt).map((e) => new Mt(e));
    for (let e of this.plugins) e.update(this);
    this.observer = new ii(this, (e, i2, n11) => rr(this, e, i2, n11), (e) => {
      this.inputState.runScrollHandlers(this, e), this.observer.intersecting && this.measure();
    }), this.inputState = new Ge2(this), this.inputState.ensureHandlers(this, this.plugins), this.docView = new re2(this), this.mountStyles(), this.updateAttrs(), this.updateState = 0, this.requestMeasure(), t3.parent && t3.parent.appendChild(this.dom);
  }
  get state() {
    return this.viewState.state;
  }
  get viewport() {
    return this.viewState.viewport;
  }
  get visibleRanges() {
    return this.viewState.visibleRanges;
  }
  get inView() {
    return this.viewState.inView;
  }
  get composing() {
    return this.inputState.composing > 0;
  }
  get compositionStarted() {
    return this.inputState.composing >= 0;
  }
  dispatch(...t3) {
    this._dispatch(t3.length == 1 && t3[0] instanceof S ? t3[0] : this.state.update(...t3));
  }
  update(t3) {
    if (this.updateState != 0) throw new Error("Calls to EditorView.update are not allowed while an update is in progress");
    let e = false, i2 = false, n11, r2 = this.state;
    for (let l9 of t3) {
      if (l9.startState != r2) throw new RangeError("Trying to update state with a transaction that doesn't start from the previous state.");
      r2 = l9.state;
    }
    if (this.destroyed) {
      this.viewState.state = r2;
      return;
    }
    if (this.observer.clear(), r2.facet(I.phrases) != this.state.facet(I.phrases)) return this.setState(r2);
    n11 = ie2.create(this, r2, t3);
    let o3 = this.viewState.scrollTarget;
    try {
      this.updateState = 2;
      for (let l9 of t3) {
        if (o3 && (o3 = o3.map(l9.changes)), l9.scrollIntoView) {
          let { main: h } = l9.state.selection;
          o3 = new ee2(h.empty ? h : x.cursor(h.head, h.head > h.anchor ? -1 : 1));
        }
        for (let h of l9.effects) h.is(Di) && (o3 = h.value);
      }
      this.viewState.update(n11, o3), this.bidiCache = fe2.update(this.bidiCache, n11.changes), n11.empty || (this.updatePlugins(n11), this.inputState.update(n11)), e = this.docView.update(n11), this.state.facet(yt) != this.styleModules && this.mountStyles(), i2 = this.updateAttrs(), this.showAnnouncements(t3), this.docView.updateSelection(e, t3.some((l9) => l9.isUserEvent("select.pointer")));
    } finally {
      this.updateState = 0;
    }
    if (n11.startState.facet(Kt) != n11.state.facet(Kt) && (this.viewState.mustMeasureContent = true), (e || i2 || o3 || this.viewState.mustEnforceCursorAssoc || this.viewState.mustMeasureContent) && this.requestMeasure(), !n11.empty) for (let l9 of this.state.facet(ze2)) l9(n11);
  }
  setState(t3) {
    if (this.updateState != 0) throw new Error("Calls to EditorView.setState are not allowed while an update is in progress");
    if (this.destroyed) {
      this.viewState.state = t3;
      return;
    }
    this.updateState = 2;
    let e = this.hasFocus;
    try {
      for (let i2 of this.plugins) i2.destroy(this);
      this.viewState = new ce2(t3), this.plugins = t3.facet(bt).map((i2) => new Mt(i2)), this.pluginMap.clear();
      for (let i2 of this.plugins) i2.update(this);
      this.docView = new re2(this), this.inputState.ensureHandlers(this, this.plugins), this.mountStyles(), this.updateAttrs(), this.bidiCache = [];
    } finally {
      this.updateState = 0;
    }
    e && this.focus(), this.requestMeasure();
  }
  updatePlugins(t3) {
    let e = t3.startState.facet(bt), i2 = t3.state.facet(bt);
    if (e != i2) {
      let n11 = [];
      for (let r2 of i2) {
        let o3 = e.indexOf(r2);
        if (o3 < 0) n11.push(new Mt(r2));
        else {
          let l9 = this.plugins[o3];
          l9.mustUpdate = t3, n11.push(l9);
        }
      }
      for (let r2 of this.plugins) r2.mustUpdate != t3 && r2.destroy(this);
      this.plugins = n11, this.pluginMap.clear(), this.inputState.ensureHandlers(this, this.plugins);
    } else for (let n11 of this.plugins) n11.mustUpdate = t3;
    for (let n11 = 0; n11 < this.plugins.length; n11++) this.plugins[n11].update(this);
  }
  measure(t3 = true) {
    if (this.destroyed) return;
    this.measureScheduled > -1 && cancelAnimationFrame(this.measureScheduled), this.measureScheduled = 0, t3 && this.observer.flush();
    let e = null;
    try {
      for (let i2 = 0; ; i2++) {
        this.updateState = 1;
        let n11 = this.viewport, r2 = this.viewState.measure(this);
        if (!r2 && !this.measureRequests.length && this.viewState.scrollTarget == null) break;
        if (i2 > 5) {
          console.warn(this.measureRequests.length ? "Measure loop restarted more than 5 times" : "Viewport failed to stabilize");
          break;
        }
        let o3 = [];
        r2 & 4 || ([this.measureRequests, o3] = [
          o3,
          this.measureRequests
        ]);
        let l9 = o3.map((f) => {
          try {
            return f.read(this);
          } catch (u2) {
            return Z2(this.state, u2), Yi;
          }
        }), h = ie2.create(this, this.state, []), a2 = false, c3 = false;
        h.flags |= r2, e ? e.flags |= r2 : e = h, this.updateState = 2, h.empty || (this.updatePlugins(h), this.inputState.update(h), this.updateAttrs(), a2 = this.docView.update(h));
        for (let f = 0; f < o3.length; f++) if (l9[f] != Yi) try {
          let u2 = o3[f];
          u2.write && u2.write(l9[f], this);
        } catch (u2) {
          Z2(this.state, u2);
        }
        if (this.viewState.scrollTarget && (this.docView.scrollIntoView(this.viewState.scrollTarget), this.viewState.scrollTarget = null, c3 = true), a2 && this.docView.updateSelection(true), this.viewport.from == n11.from && this.viewport.to == n11.to && !c3 && this.measureRequests.length == 0) break;
      }
    } finally {
      this.updateState = 0, this.measureScheduled = -1;
    }
    if (e && !e.empty) for (let i2 of this.state.facet(ze2)) i2(e);
  }
  get themeClasses() {
    return ti + " " + (this.state.facet(Qe2) ? Xs : Us) + " " + this.state.facet(Kt);
  }
  updateAttrs() {
    let t3 = Ui(this, Rs, {
      class: "cm-editor" + (this.hasFocus ? " cm-focused " : " ") + this.themeClasses
    }), e = {
      spellcheck: "false",
      autocorrect: "off",
      autocapitalize: "off",
      translate: "no",
      contenteditable: this.state.facet(Nt) ? "true" : "false",
      class: "cm-content",
      style: `${g2.tabSize}: ${this.state.tabSize}`,
      role: "textbox",
      "aria-multiline": "true"
    };
    this.state.readOnly && (e["aria-readonly"] = "true"), Ui(this, bi, e);
    let i2 = this.observer.ignore(() => {
      let n11 = Ve2(this.contentDOM, this.contentAttrs, e), r2 = Ve2(this.dom, this.editorAttrs, t3);
      return n11 || r2;
    });
    return this.editorAttrs = t3, this.contentAttrs = e, i2;
  }
  showAnnouncements(t3) {
    let e = true;
    for (let i2 of t3) for (let n11 of i2.effects) if (n11.is(s41.announce)) {
      e && (this.announceDOM.textContent = ""), e = false;
      let r2 = this.announceDOM.appendChild(document.createElement("div"));
      r2.textContent = n11.value;
    }
  }
  mountStyles() {
    this.styleModules = this.state.facet(yt), T2.mount(this.root, this.styleModules.concat(ir).reverse());
  }
  readMeasured() {
    if (this.updateState == 2) throw new Error("Reading the editor layout isn't allowed during an update");
    this.updateState == 0 && this.measureScheduled > -1 && this.measure(false);
  }
  requestMeasure(t3) {
    if (this.measureScheduled < 0 && (this.measureScheduled = requestAnimationFrame(() => this.measure())), t3) {
      if (t3.key != null) {
        for (let e = 0; e < this.measureRequests.length; e++) if (this.measureRequests[e].key === t3.key) {
          this.measureRequests[e] = t3;
          return;
        }
      }
      this.measureRequests.push(t3);
    }
  }
  plugin(t3) {
    let e = this.pluginMap.get(t3);
    return (e === void 0 || e && e.spec != t3) && this.pluginMap.set(t3, e = this.plugins.find((i2) => i2.spec == t3) || null), e && e.update(this).value;
  }
  get documentTop() {
    return this.contentDOM.getBoundingClientRect().top + this.viewState.paddingTop;
  }
  get documentPadding() {
    return {
      top: this.viewState.paddingTop,
      bottom: this.viewState.paddingBottom
    };
  }
  elementAtHeight(t3) {
    return this.readMeasured(), this.viewState.elementAtHeight(t3);
  }
  lineBlockAtHeight(t3) {
    return this.readMeasured(), this.viewState.lineBlockAtHeight(t3);
  }
  get viewportLineBlocks() {
    return this.viewState.viewportLines;
  }
  lineBlockAt(t3) {
    return this.viewState.lineBlockAt(t3);
  }
  get contentHeight() {
    return this.viewState.contentHeight;
  }
  moveByChar(t3, e, i2) {
    return ve2(this, t3, Bi(this, t3, e, i2));
  }
  moveByGroup(t3, e) {
    return ve2(this, t3, Bi(this, t3, e, (i2) => zn(this, t3.head, i2)));
  }
  moveToLineBoundary(t3, e, i2 = true) {
    return Wn(this, t3, e, i2);
  }
  moveVertically(t3, e, i2) {
    return ve2(this, t3, Fn(this, t3, e, i2));
  }
  domAtPos(t3) {
    return this.docView.domAtPos(t3);
  }
  posAtDOM(t3, e = 0) {
    return this.docView.posFromDOM(t3, e);
  }
  posAtCoords(t3, e = true) {
    return this.readMeasured(), Fs(this, t3, e);
  }
  coordsAtPos(t3, e = 1) {
    this.readMeasured();
    let i2 = this.docView.coordsAt(t3, e);
    if (!i2 || i2.left == i2.right) return i2;
    let n11 = this.state.doc.lineAt(t3), r2 = this.bidiSpans(n11), o3 = r2[Q2.find(r2, t3 - n11.from, -1, e)];
    return ge2(i2, o3.dir == O2.LTR == e > 0);
  }
  get defaultCharacterWidth() {
    return this.viewState.heightOracle.charWidth;
  }
  get defaultLineHeight() {
    return this.viewState.heightOracle.lineHeight;
  }
  get textDirection() {
    return this.viewState.defaultTextDirection;
  }
  textDirectionAt(t3) {
    return !this.state.facet(Os) || t3 < this.viewport.from || t3 > this.viewport.to ? this.textDirection : (this.readMeasured(), this.docView.textDirectionAt(t3));
  }
  get lineWrapping() {
    return this.viewState.heightOracle.lineWrapping;
  }
  bidiSpans(t3) {
    if (t3.length > ar) return Ps(t3.length);
    let e = this.textDirectionAt(t3.from);
    for (let n11 of this.bidiCache) if (n11.from == t3.from && n11.dir == e) return n11.order;
    let i2 = Hs(t3.text, e);
    return this.bidiCache.push(new fe2(t3.from, t3.to, e, i2)), i2;
  }
  get hasFocus() {
    var t3;
    return (document.hasFocus() || g2.safari && ((t3 = this.inputState) === null || t3 === void 0 ? void 0 : t3.lastContextMenu) > Date.now() - 3e4) && this.root.activeElement == this.contentDOM;
  }
  focus() {
    this.observer.ignore(() => {
      us(this.contentDOM), this.docView.updateSelection();
    });
  }
  destroy() {
    for (let t3 of this.plugins) t3.destroy(this);
    this.plugins = [], this.inputState.destroy(), this.dom.remove(), this.observer.destroy(), this.measureScheduled > -1 && cancelAnimationFrame(this.measureScheduled), this.destroyed = true;
  }
  static scrollIntoView(t3, e = {}) {
    return Di.of(new ee2(typeof t3 == "number" ? x.cursor(t3) : t3, e.y, e.x, e.yMargin, e.xMargin));
  }
  static domEventHandlers(t3) {
    return P2.define(() => ({}), {
      eventHandlers: t3
    });
  }
  static theme(t3, e) {
    let i2 = T2.newName(), n11 = [
      Kt.of(i2),
      yt.of(ei(`.${i2}`, t3))
    ];
    return e && e.dark && n11.push(Qe2.of(true)), n11;
  }
  static baseTheme(t3) {
    return lt.lowest(yt.of(ei("." + ti, t3, Js)));
  }
};
M2.styleModule = yt;
M2.inputHandler = Ts;
M2.perLineTextDirection = Os;
M2.exceptionSink = Ds;
M2.updateListener = ze2;
M2.editable = Nt;
M2.mouseSelectionStyle = As;
M2.dragMovesSelection = ks;
M2.clickAddsSelectionRange = Ms;
M2.decorations = Ht;
M2.atomicRanges = Ls;
M2.scrollMargins = Es;
M2.darkTheme = Qe2;
M2.contentAttributes = bi;
M2.editorAttributes = Rs;
M2.lineWrapping = M2.contentAttributes.of({
  class: "cm-lineWrapping"
});
M2.announce = v.define();
var ar = 4096;
var Yi = {};
var fe2 = class s42 {
  constructor(t3, e, i2, n11) {
    this.from = t3, this.to = e, this.dir = i2, this.order = n11;
  }
  static update(t3, e) {
    if (e.empty) return t3;
    let i2 = [], n11 = t3.length ? t3[t3.length - 1].dir : O2.LTR;
    for (let r2 = Math.max(0, t3.length - 10); r2 < t3.length; r2++) {
      let o3 = t3[r2];
      o3.dir == n11 && !e.touchesRange(o3.from, o3.to) && i2.push(new s42(e.mapPos(o3.from, 1), e.mapPos(o3.to, -1), o3.dir, o3.order));
    }
    return i2;
  }
};
function Ui(s45, t3, e) {
  for (let i2 = s45.state.facet(t3), n11 = i2.length - 1; n11 >= 0; n11--) {
    let r2 = i2[n11], o3 = typeof r2 == "function" ? r2(s45) : r2;
    o3 && Pe2(o3, e);
  }
  return e;
}
var cr = g2.mac ? "mac" : g2.windows ? "win" : g2.linux ? "linux" : "key";
function fr(s45, t3) {
  let e = s45.split(/-(?!$)/), i2 = e[e.length - 1];
  i2 == "Space" && (i2 = " ");
  let n11, r2, o3, l9;
  for (let h = 0; h < e.length - 1; ++h) {
    let a2 = e[h];
    if (/^(cmd|meta|m)$/i.test(a2)) l9 = true;
    else if (/^a(lt)?$/i.test(a2)) n11 = true;
    else if (/^(c|ctrl|control)$/i.test(a2)) r2 = true;
    else if (/^s(hift)?$/i.test(a2)) o3 = true;
    else if (/^mod$/i.test(a2)) t3 == "mac" ? l9 = true : r2 = true;
    else throw new Error("Unrecognized modifier name: " + a2);
  }
  return n11 && (i2 = "Alt-" + i2), r2 && (i2 = "Ctrl-" + i2), l9 && (i2 = "Meta-" + i2), o3 && (i2 = "Shift-" + i2), i2;
}
function Se2(s45, t3, e) {
  return t3.altKey && (s45 = "Alt-" + s45), t3.ctrlKey && (s45 = "Ctrl-" + s45), t3.metaKey && (s45 = "Meta-" + s45), e !== false && t3.shiftKey && (s45 = "Shift-" + s45), s45;
}
var dr = M2.domEventHandlers({
  keydown(s45, t3) {
    return Qs(Zs(t3.state), s45, t3, "editor");
  }
});
var ur = y.define({
  enables: dr
});
var Xi = /* @__PURE__ */ new WeakMap();
function Zs(s45) {
  let t3 = s45.facet(ur), e = Xi.get(t3);
  return e || Xi.set(t3, e = mr(t3.reduce((i2, n11) => i2.concat(n11), []))), e;
}
var U2 = null;
var pr = 4e3;
function mr(s45, t3 = cr) {
  let e = /* @__PURE__ */ Object.create(null), i2 = /* @__PURE__ */ Object.create(null), n11 = (o3, l9) => {
    let h = i2[o3];
    if (h == null) i2[o3] = l9;
    else if (h != l9) throw new Error("Key binding " + o3 + " is used both as a regular binding and as a multi-stroke prefix");
  }, r2 = (o3, l9, h, a2) => {
    let c3 = e[o3] || (e[o3] = /* @__PURE__ */ Object.create(null)), f = l9.split(/ (?!$)/).map((p2) => fr(p2, t3));
    for (let p2 = 1; p2 < f.length; p2++) {
      let m4 = f.slice(0, p2).join(" ");
      n11(m4, true), c3[m4] || (c3[m4] = {
        preventDefault: true,
        commands: [
          (b4) => {
            let y4 = U2 = {
              view: b4,
              prefix: m4,
              scope: o3
            };
            return setTimeout(() => {
              U2 == y4 && (U2 = null);
            }, pr), true;
          }
        ]
      });
    }
    let u2 = f.join(" ");
    n11(u2, false);
    let d = c3[u2] || (c3[u2] = {
      preventDefault: false,
      commands: []
    });
    d.commands.push(h), a2 && (d.preventDefault = true);
  };
  for (let o3 of s45) {
    let l9 = o3[t3] || o3.key;
    if (l9) for (let h of o3.scope ? o3.scope.split(" ") : [
      "editor"
    ]) r2(h, l9, o3.run, o3.preventDefault), o3.shift && r2(h, "Shift-" + l9, o3.shift, o3.preventDefault);
  }
  return e;
}
function Qs(s45, t3, e, i2) {
  let n11 = g(t3), r2 = n11.length == 1 && n11 != " ", o3 = "", l9 = false;
  U2 && U2.view == e && U2.scope == i2 && (o3 = U2.prefix + " ", (l9 = qs.indexOf(t3.keyCode) < 0) && (U2 = null));
  let h = (f) => {
    if (f) {
      for (let u2 of f.commands) if (u2(e)) return true;
      f.preventDefault && (l9 = true);
    }
    return false;
  }, a2 = s45[i2], c3;
  if (a2) {
    if (h(a2[o3 + Se2(n11, t3, !r2)])) return true;
    if (r2 && (t3.shiftKey || t3.altKey || t3.metaKey) && (c3 = t[t3.keyCode]) && c3 != n11) {
      if (h(a2[o3 + Se2(c3, t3, true)])) return true;
    } else if (r2 && t3.shiftKey && h(a2[o3 + Se2(n11, t3, true)])) return true;
  }
  return l9;
}
var tn = !g2.ios;
var vt = y.define({
  combine(s45) {
    return ht(s45, {
      cursorBlinkRate: 1200,
      drawRangeCursor: true
    }, {
      cursorBlinkRate: (t3, e) => Math.min(t3, e),
      drawRangeCursor: (t3, e) => t3 || e
    });
  }
});
var de2 = class {
  constructor(t3, e, i2, n11, r2) {
    this.left = t3, this.top = e, this.width = i2, this.height = n11, this.className = r2;
  }
  draw() {
    let t3 = document.createElement("div");
    return t3.className = this.className, this.adjust(t3), t3;
  }
  adjust(t3) {
    t3.style.left = this.left + "px", t3.style.top = this.top + "px", this.width >= 0 && (t3.style.width = this.width + "px"), t3.style.height = this.height + "px";
  }
  eq(t3) {
    return this.left == t3.left && this.top == t3.top && this.width == t3.width && this.height == t3.height && this.className == t3.className;
  }
};
var gr = P2.fromClass(class {
  constructor(s45) {
    this.view = s45, this.rangePieces = [], this.cursors = [], this.measureReq = {
      read: this.readPos.bind(this),
      write: this.drawSel.bind(this)
    }, this.selectionLayer = s45.scrollDOM.appendChild(document.createElement("div")), this.selectionLayer.className = "cm-selectionLayer", this.selectionLayer.setAttribute("aria-hidden", "true"), this.cursorLayer = s45.scrollDOM.appendChild(document.createElement("div")), this.cursorLayer.className = "cm-cursorLayer", this.cursorLayer.setAttribute("aria-hidden", "true"), s45.requestMeasure(this.measureReq), this.setBlinkRate();
  }
  setBlinkRate() {
    this.cursorLayer.style.animationDuration = this.view.state.facet(vt).cursorBlinkRate + "ms";
  }
  update(s45) {
    let t3 = s45.startState.facet(vt) != s45.state.facet(vt);
    (t3 || s45.selectionSet || s45.geometryChanged || s45.viewportChanged) && this.view.requestMeasure(this.measureReq), s45.transactions.some((e) => e.scrollIntoView) && (this.cursorLayer.style.animationName = this.cursorLayer.style.animationName == "cm-blink" ? "cm-blink2" : "cm-blink"), t3 && this.setBlinkRate();
  }
  readPos() {
    let { state: s45 } = this.view, t3 = s45.facet(vt), e = s45.selection.ranges.map((n11) => n11.empty ? [] : yr(this.view, n11)).reduce((n11, r2) => n11.concat(r2)), i2 = [];
    for (let n11 of s45.selection.ranges) {
      let r2 = n11 == s45.selection.main;
      if (n11.empty ? !r2 || tn : t3.drawRangeCursor) {
        let o3 = wr(this.view, n11, r2);
        o3 && i2.push(o3);
      }
    }
    return {
      rangePieces: e,
      cursors: i2
    };
  }
  drawSel({ rangePieces: s45, cursors: t3 }) {
    if (s45.length != this.rangePieces.length || s45.some((e, i2) => !e.eq(this.rangePieces[i2]))) {
      this.selectionLayer.textContent = "";
      for (let e of s45) this.selectionLayer.appendChild(e.draw());
      this.rangePieces = s45;
    }
    if (t3.length != this.cursors.length || t3.some((e, i2) => !e.eq(this.cursors[i2]))) {
      let e = this.cursorLayer.children;
      if (e.length !== t3.length) {
        this.cursorLayer.textContent = "";
        for (let i2 of t3) this.cursorLayer.appendChild(i2.draw());
      } else t3.forEach((i2, n11) => i2.adjust(e[n11]));
      this.cursors = t3;
    }
  }
  destroy() {
    this.selectionLayer.remove(), this.cursorLayer.remove();
  }
});
var en = {
  ".cm-line": {
    "& ::selection": {
      backgroundColor: "transparent !important"
    },
    "&::selection": {
      backgroundColor: "transparent !important"
    }
  }
};
tn && (en[".cm-line"].caretColor = "transparent !important");
var br = lt.highest(M2.theme(en));
function sn(s45) {
  let t3 = s45.scrollDOM.getBoundingClientRect();
  return {
    left: (s45.textDirection == O2.LTR ? t3.left : t3.right - s45.scrollDOM.clientWidth) - s45.scrollDOM.scrollLeft,
    top: t3.top - s45.scrollDOM.scrollTop
  };
}
function Ji(s45, t3, e) {
  let i2 = x.cursor(t3);
  return {
    from: Math.max(e.from, s45.moveToLineBoundary(i2, false, true).from),
    to: Math.min(e.to, s45.moveToLineBoundary(i2, true, true).from),
    type: D2.Text
  };
}
function Zi(s45, t3) {
  let e = s45.lineBlockAt(t3);
  if (Array.isArray(e.type)) {
    for (let i2 of e.type) if (i2.to > t3 || i2.to == t3 && (i2.to == e.to || i2.type == D2.Text)) return i2;
  }
  return e;
}
function yr(s45, t3) {
  if (t3.to <= s45.viewport.from || t3.from >= s45.viewport.to) return [];
  let e = Math.max(t3.from, s45.viewport.from), i2 = Math.min(t3.to, s45.viewport.to), n11 = s45.textDirection == O2.LTR, r2 = s45.contentDOM, o3 = r2.getBoundingClientRect(), l9 = sn(s45), h = globalThis.getComputedStyle(r2.firstChild), a2 = o3.left + parseInt(h.paddingLeft) + Math.min(0, parseInt(h.textIndent)), c3 = o3.right - parseInt(h.paddingRight), f = Zi(s45, e), u2 = Zi(s45, i2), d = f.type == D2.Text ? f : null, p2 = u2.type == D2.Text ? u2 : null;
  if (s45.lineWrapping && (d && (d = Ji(s45, e, d)), p2 && (p2 = Ji(s45, i2, p2))), d && p2 && d.from == p2.from) return b4(y4(t3.from, t3.to, d));
  {
    let v3 = d ? y4(t3.from, null, d) : k4(f, false), w5 = p2 ? y4(null, t3.to, p2) : k4(u2, true), L5 = [];
    return (d || f).to < (p2 || u2).from - 1 ? L5.push(m4(a2, v3.bottom, c3, w5.top)) : v3.bottom < w5.top && s45.elementAtHeight((v3.bottom + w5.top) / 2).type == D2.Text && (v3.bottom = w5.top = (v3.bottom + w5.top) / 2), b4(v3).concat(L5).concat(b4(w5));
  }
  function m4(v3, w5, L5, j4) {
    return new de2(v3 - l9.left, w5 - l9.top - 0.01, L5 - v3, j4 - w5 + 0.01, "cm-selectionBackground");
  }
  function b4({ top: v3, bottom: w5, horizontal: L5 }) {
    let j4 = [];
    for (let G3 = 0; G3 < L5.length; G3 += 2) j4.push(m4(L5[G3], v3, L5[G3 + 1], w5));
    return j4;
  }
  function y4(v3, w5, L5) {
    let j4 = 1e9, G3 = -1e9, Wt2 = [];
    function vi(st4, $5, lt3, nt4, mt3) {
      let _5 = s45.coordsAtPos(st4, st4 == L5.to ? -2 : 2), Y5 = s45.coordsAtPos(lt3, lt3 == L5.from ? 2 : -2);
      j4 = Math.min(_5.top, Y5.top, j4), G3 = Math.max(_5.bottom, Y5.bottom, G3), mt3 == O2.LTR ? Wt2.push(n11 && $5 ? a2 : _5.left, n11 && nt4 ? c3 : Y5.right) : Wt2.push(!n11 && nt4 ? a2 : Y5.left, !n11 && $5 ? c3 : _5.right);
    }
    let zt = v3 ?? L5.from, Ft2 = w5 ?? L5.to;
    for (let st4 of s45.visibleRanges) if (st4.to > zt && st4.from < Ft2) for (let $5 = Math.max(st4.from, zt), lt3 = Math.min(st4.to, Ft2); ; ) {
      let nt4 = s45.state.doc.lineAt($5);
      for (let mt3 of s45.bidiSpans(nt4)) {
        let _5 = mt3.from + nt4.from, Y5 = mt3.to + nt4.from;
        if (_5 >= lt3) break;
        Y5 > $5 && vi(Math.max(_5, $5), v3 == null && _5 <= zt, Math.min(Y5, lt3), w5 == null && Y5 >= Ft2, mt3.dir);
      }
      if ($5 = nt4.to + 1, $5 >= lt3) break;
    }
    return Wt2.length == 0 && vi(zt, v3 == null, Ft2, w5 == null, s45.textDirection), {
      top: j4,
      bottom: G3,
      horizontal: Wt2
    };
  }
  function k4(v3, w5) {
    let L5 = o3.top + (w5 ? v3.top : v3.bottom);
    return {
      top: L5,
      bottom: L5,
      horizontal: []
    };
  }
}
function wr(s45, t3, e) {
  let i2 = s45.coordsAtPos(t3.head, t3.assoc || 1);
  if (!i2) return null;
  let n11 = sn(s45);
  return new de2(i2.left - n11.left, i2.top - n11.top, -1, i2.bottom - i2.top, e ? "cm-cursor cm-cursor-primary" : "cm-cursor cm-cursor-secondary");
}
var nn = v.define({
  map(s45, t3) {
    return s45 == null ? null : t3.mapPos(s45);
  }
});
var xt = $.define({
  create() {
    return null;
  },
  update(s45, t3) {
    return s45 != null && (s45 = t3.changes.mapPos(s45)), t3.effects.reduce((e, i2) => i2.is(nn) ? i2.value : e, s45);
  }
});
var vr = P2.fromClass(class {
  constructor(s45) {
    this.view = s45, this.cursor = null, this.measureReq = {
      read: this.readPos.bind(this),
      write: this.drawCursor.bind(this)
    };
  }
  update(s45) {
    var t3;
    let e = s45.state.field(xt);
    e == null ? this.cursor != null && ((t3 = this.cursor) === null || t3 === void 0 || t3.remove(), this.cursor = null) : (this.cursor || (this.cursor = this.view.scrollDOM.appendChild(document.createElement("div")), this.cursor.className = "cm-dropCursor"), (s45.startState.field(xt) != e || s45.docChanged || s45.geometryChanged) && this.view.requestMeasure(this.measureReq));
  }
  readPos() {
    let s45 = this.view.state.field(xt), t3 = s45 != null && this.view.coordsAtPos(s45);
    if (!t3) return null;
    let e = this.view.scrollDOM.getBoundingClientRect();
    return {
      left: t3.left - e.left + this.view.scrollDOM.scrollLeft,
      top: t3.top - e.top + this.view.scrollDOM.scrollTop,
      height: t3.bottom - t3.top
    };
  }
  drawCursor(s45) {
    this.cursor && (s45 ? (this.cursor.style.left = s45.left + "px", this.cursor.style.top = s45.top + "px", this.cursor.style.height = s45.height + "px") : this.cursor.style.left = "-100000px");
  }
  destroy() {
    this.cursor && this.cursor.remove();
  }
  setDropPos(s45) {
    this.view.state.field(xt) != s45 && this.view.dispatch({
      effects: nn.of(s45)
    });
  }
}, {
  eventHandlers: {
    dragover(s45) {
      this.setDropPos(this.view.posAtCoords({
        x: s45.clientX,
        y: s45.clientY
      }));
    },
    dragleave(s45) {
      (s45.target == this.view.contentDOM || !this.view.contentDOM.contains(s45.relatedTarget)) && this.setDropPos(null);
    },
    dragend() {
      this.setDropPos(null);
    },
    drop() {
      this.setDropPos(null);
    }
  }
});
var ni = /x/.unicode != null ? "gu" : "g";
var Sr = new RegExp(`[\x00-\x08
-\x7F-\x9F\xAD\u061C\u200B\u200E\u200F\u2028\u2029\u202D\u202E\uFEFF\uFFF9-\uFFFC]`, ni);
var Ce2 = null;
function Mr() {
  var s45;
  if (Ce2 == null && typeof document < "u" && document.body) {
    let t3 = document.body.style;
    Ce2 = ((s45 = t3.tabSize) !== null && s45 !== void 0 ? s45 : t3.MozTabSize) != null;
  }
  return Ce2 || false;
}
var Gt = y.define({
  combine(s45) {
    let t3 = ht(s45, {
      render: null,
      specialChars: Sr,
      addSpecialChars: null
    });
    return (t3.replaceTabs = !Mr()) && (t3.specialChars = new RegExp("	|" + t3.specialChars.source, ni)), t3.addSpecialChars && (t3.specialChars = new RegExp(t3.specialChars.source + "|" + t3.addSpecialChars.source, ni)), t3;
  }
});
var es = P2.fromClass(class {
  constructor() {
    this.height = 1e3, this.attrs = {
      style: "padding-bottom: 1000px"
    };
  }
  update(s45) {
    let t3 = s45.view.viewState.editorHeight - s45.view.defaultLineHeight;
    t3 != this.height && (this.height = t3, this.attrs = {
      style: `padding-bottom: ${t3}px`
    });
  }
});
var Tr = C2.line({
  class: "cm-activeLine"
});
var Or = P2.fromClass(class {
  constructor(s45) {
    this.decorations = this.getDeco(s45);
  }
  update(s45) {
    (s45.docChanged || s45.selectionSet) && (this.decorations = this.getDeco(s45.view));
  }
  getDeco(s45) {
    let t3 = -1, e = [];
    for (let i2 of s45.state.selection.ranges) {
      if (!i2.empty) return C2.none;
      let n11 = s45.lineBlockAt(i2.head);
      n11.from > t3 && (e.push(Tr.range(n11.from)), t3 = n11.from);
    }
    return C2.set(e);
  }
}, {
  decorations: (s45) => s45.decorations
});
var Me2 = "-10000px";
var ue2 = class {
  constructor(t3, e, i2) {
    this.facet = e, this.createTooltipView = i2, this.input = t3.state.facet(e), this.tooltips = this.input.filter((n11) => n11), this.tooltipViews = this.tooltips.map(i2);
  }
  update(t3) {
    let e = t3.state.facet(this.facet), i2 = e.filter((r2) => r2);
    if (e === this.input) {
      for (let r2 of this.tooltipViews) r2.update && r2.update(t3);
      return false;
    }
    let n11 = [];
    for (let r2 = 0; r2 < i2.length; r2++) {
      let o3 = i2[r2], l9 = -1;
      if (o3) {
        for (let h = 0; h < this.tooltips.length; h++) {
          let a2 = this.tooltips[h];
          a2 && a2.create == o3.create && (l9 = h);
        }
        if (l9 < 0) n11[r2] = this.createTooltipView(o3);
        else {
          let h = n11[r2] = this.tooltipViews[l9];
          h.update && h.update(t3);
        }
      }
    }
    for (let r2 of this.tooltipViews) n11.indexOf(r2) < 0 && r2.dom.remove();
    return this.input = e, this.tooltips = i2, this.tooltipViews = n11, true;
  }
};
function Pr() {
  return {
    top: 0,
    left: 0,
    bottom: innerHeight,
    right: innerWidth
  };
}
var $t = y.define({
  combine: (s45) => {
    var t3, e, i2;
    return {
      position: g2.ios ? "absolute" : ((t3 = s45.find((n11) => n11.position)) === null || t3 === void 0 ? void 0 : t3.position) || "fixed",
      parent: ((e = s45.find((n11) => n11.parent)) === null || e === void 0 ? void 0 : e.parent) || null,
      tooltipSpace: ((i2 = s45.find((n11) => n11.tooltipSpace)) === null || i2 === void 0 ? void 0 : i2.tooltipSpace) || Pr
    };
  }
});
var wi = P2.fromClass(class {
  constructor(s45) {
    var t3;
    this.view = s45, this.inView = true, this.lastTransaction = 0, this.measureTimeout = -1;
    let e = s45.state.facet($t);
    this.position = e.position, this.parent = e.parent, this.classes = s45.themeClasses, this.createContainer(), this.measureReq = {
      read: this.readMeasure.bind(this),
      write: this.writeMeasure.bind(this),
      key: this
    }, this.manager = new ue2(s45, rn, (i2) => this.createTooltip(i2)), this.intersectionObserver = typeof IntersectionObserver == "function" ? new IntersectionObserver((i2) => {
      Date.now() > this.lastTransaction - 50 && i2.length > 0 && i2[i2.length - 1].intersectionRatio < 1 && this.measureSoon();
    }, {
      threshold: [
        1
      ]
    }) : null, this.observeIntersection(), (t3 = s45.dom.ownerDocument.defaultView) === null || t3 === void 0 || t3.addEventListener("resize", this.measureSoon = this.measureSoon.bind(this)), this.maybeMeasure();
  }
  createContainer() {
    this.parent ? (this.container = document.createElement("div"), this.container.style.position = "relative", this.container.className = this.view.themeClasses, this.parent.appendChild(this.container)) : this.container = this.view.dom;
  }
  observeIntersection() {
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect();
      for (let s45 of this.manager.tooltipViews) this.intersectionObserver.observe(s45.dom);
    }
  }
  measureSoon() {
    this.measureTimeout < 0 && (this.measureTimeout = setTimeout(() => {
      this.measureTimeout = -1, this.maybeMeasure();
    }, 50));
  }
  update(s45) {
    s45.transactions.length && (this.lastTransaction = Date.now());
    let t3 = this.manager.update(s45);
    t3 && this.observeIntersection();
    let e = t3 || s45.geometryChanged, i2 = s45.state.facet($t);
    if (i2.position != this.position) {
      this.position = i2.position;
      for (let n11 of this.manager.tooltipViews) n11.dom.style.position = this.position;
      e = true;
    }
    if (i2.parent != this.parent) {
      this.parent && this.container.remove(), this.parent = i2.parent, this.createContainer();
      for (let n11 of this.manager.tooltipViews) this.container.appendChild(n11.dom);
      e = true;
    } else this.parent && this.view.themeClasses != this.classes && (this.classes = this.container.className = this.view.themeClasses);
    e && this.maybeMeasure();
  }
  createTooltip(s45) {
    let t3 = s45.create(this.view);
    if (t3.dom.classList.add("cm-tooltip"), s45.arrow && !t3.dom.querySelector(".cm-tooltip > .cm-tooltip-arrow")) {
      let e = document.createElement("div");
      e.className = "cm-tooltip-arrow", t3.dom.appendChild(e);
    }
    return t3.dom.style.position = this.position, t3.dom.style.top = Me2, this.container.appendChild(t3.dom), t3.mount && t3.mount(this.view), t3;
  }
  destroy() {
    var s45, t3;
    (s45 = this.view.dom.ownerDocument.defaultView) === null || s45 === void 0 || s45.removeEventListener("resize", this.measureSoon);
    for (let { dom: e } of this.manager.tooltipViews) e.remove();
    (t3 = this.intersectionObserver) === null || t3 === void 0 || t3.disconnect(), clearTimeout(this.measureTimeout);
  }
  readMeasure() {
    let s45 = this.view.dom.getBoundingClientRect();
    return {
      editor: s45,
      parent: this.parent ? this.container.getBoundingClientRect() : s45,
      pos: this.manager.tooltips.map((t3, e) => {
        let i2 = this.manager.tooltipViews[e];
        return i2.getCoords ? i2.getCoords(t3.pos) : this.view.coordsAtPos(t3.pos);
      }),
      size: this.manager.tooltipViews.map(({ dom: t3 }) => t3.getBoundingClientRect()),
      space: this.view.state.facet($t).tooltipSpace(this.view)
    };
  }
  writeMeasure(s45) {
    let { editor: t3, space: e } = s45, i2 = [];
    for (let n11 = 0; n11 < this.manager.tooltips.length; n11++) {
      let r2 = this.manager.tooltips[n11], o3 = this.manager.tooltipViews[n11], { dom: l9 } = o3, h = s45.pos[n11], a2 = s45.size[n11];
      if (!h || h.bottom <= Math.max(t3.top, e.top) || h.top >= Math.min(t3.bottom, e.bottom) || h.right < Math.max(t3.left, e.left) - 0.1 || h.left > Math.min(t3.right, e.right) + 0.1) {
        l9.style.top = Me2;
        continue;
      }
      let c3 = r2.arrow ? o3.dom.querySelector(".cm-tooltip-arrow") : null, f = c3 ? 7 : 0, u2 = a2.right - a2.left, d = a2.bottom - a2.top, p2 = o3.offset || Nr, m4 = this.view.textDirection == O2.LTR, b4 = a2.width > e.right - e.left ? m4 ? e.left : e.right - a2.width : m4 ? Math.min(h.left - (c3 ? 14 : 0) + p2.x, e.right - u2) : Math.max(e.left, h.left - u2 + (c3 ? 14 : 0) - p2.x), y4 = !!r2.above;
      !r2.strictSide && (y4 ? h.top - (a2.bottom - a2.top) - p2.y < e.top : h.bottom + (a2.bottom - a2.top) + p2.y > e.bottom) && y4 == e.bottom - h.bottom > h.top - e.top && (y4 = !y4);
      let k4 = y4 ? h.top - d - f - p2.y : h.bottom + f + p2.y, v3 = b4 + u2;
      if (o3.overlap !== true) for (let w5 of i2) w5.left < v3 && w5.right > b4 && w5.top < k4 + d && w5.bottom > k4 && (k4 = y4 ? w5.top - d - 2 - f : w5.bottom + f + 2);
      this.position == "absolute" ? (l9.style.top = k4 - s45.parent.top + "px", l9.style.left = b4 - s45.parent.left + "px") : (l9.style.top = k4 + "px", l9.style.left = b4 + "px"), c3 && (c3.style.left = `${h.left + (m4 ? p2.x : -p2.x) - (b4 + 14 - 7)}px`), o3.overlap !== true && i2.push({
        left: b4,
        top: k4,
        right: v3,
        bottom: k4 + d
      }), l9.classList.toggle("cm-tooltip-above", y4), l9.classList.toggle("cm-tooltip-below", !y4), o3.positioned && o3.positioned();
    }
  }
  maybeMeasure() {
    if (this.manager.tooltips.length && (this.view.inView && this.view.requestMeasure(this.measureReq), this.inView != this.view.inView && (this.inView = this.view.inView, !this.inView))) for (let s45 of this.manager.tooltipViews) s45.dom.style.top = Me2;
  }
}, {
  eventHandlers: {
    scroll() {
      this.maybeMeasure();
    }
  }
});
var Vr = M2.baseTheme({
  ".cm-tooltip": {
    zIndex: 100
  },
  "&light .cm-tooltip": {
    border: "1px solid #bbb",
    backgroundColor: "#f5f5f5"
  },
  "&light .cm-tooltip-section:not(:first-child)": {
    borderTop: "1px solid #bbb"
  },
  "&dark .cm-tooltip": {
    backgroundColor: "#333338",
    color: "white"
  },
  ".cm-tooltip-arrow": {
    height: "7px",
    width: "14px",
    position: "absolute",
    zIndex: -1,
    overflow: "hidden",
    "&:before, &:after": {
      content: "''",
      position: "absolute",
      width: 0,
      height: 0,
      borderLeft: "7px solid transparent",
      borderRight: "7px solid transparent"
    },
    ".cm-tooltip-above &": {
      bottom: "-7px",
      "&:before": {
        borderTop: "7px solid #bbb"
      },
      "&:after": {
        borderTop: "7px solid #f5f5f5",
        bottom: "1px"
      }
    },
    ".cm-tooltip-below &": {
      top: "-7px",
      "&:before": {
        borderBottom: "7px solid #bbb"
      },
      "&:after": {
        borderBottom: "7px solid #f5f5f5",
        top: "1px"
      }
    }
  },
  "&dark .cm-tooltip .cm-tooltip-arrow": {
    "&:before": {
      borderTopColor: "#333338",
      borderBottomColor: "#333338"
    },
    "&:after": {
      borderTopColor: "transparent",
      borderBottomColor: "transparent"
    }
  }
});
var Nr = {
  x: 0,
  y: 0
};
var rn = y.define({
  enables: [
    wi,
    Vr
  ]
});
var Pt = y.define();
var ai = class s43 {
  constructor(t3) {
    this.view = t3, this.mounted = false, this.dom = document.createElement("div"), this.dom.classList.add("cm-tooltip-hover"), this.manager = new ue2(t3, Pt, (e) => this.createHostedView(e));
  }
  static create(t3) {
    return new s43(t3);
  }
  createHostedView(t3) {
    let e = t3.create(this.view);
    return e.dom.classList.add("cm-tooltip-section"), this.dom.appendChild(e.dom), this.mounted && e.mount && e.mount(this.view), e;
  }
  mount(t3) {
    for (let e of this.manager.tooltipViews) e.mount && e.mount(t3);
    this.mounted = true;
  }
  positioned() {
    for (let t3 of this.manager.tooltipViews) t3.positioned && t3.positioned();
  }
  update(t3) {
    this.manager.update(t3);
  }
};
var Wr = rn.compute([
  Pt
], (s45) => {
  let t3 = s45.facet(Pt).filter((e) => e);
  return t3.length === 0 ? null : {
    pos: Math.min(...t3.map((e) => e.pos)),
    end: Math.max(...t3.filter((e) => e.end != null).map((e) => e.end)),
    create: ai.create,
    above: t3[0].above,
    arrow: t3.some((e) => e.arrow)
  };
});
function ho(s45, t3) {
  let e = s45.plugin(wi);
  if (!e) return null;
  let i2 = e.manager.tooltips.indexOf(t3);
  return i2 < 0 ? null : e.manager.tooltipViews[i2];
}
var on = v.define();
var co = on.of(null);
var fi = y.define({
  combine(s45) {
    let t3, e;
    for (let i2 of s45) t3 = t3 || i2.topContainer, e = e || i2.bottomContainer;
    return {
      topContainer: t3,
      bottomContainer: e
    };
  }
});
var ln = P2.fromClass(class {
  constructor(s45) {
    this.input = s45.state.facet(ns), this.specs = this.input.filter((e) => e), this.panels = this.specs.map((e) => e(s45));
    let t3 = s45.state.facet(fi);
    this.top = new ct(s45, true, t3.topContainer), this.bottom = new ct(s45, false, t3.bottomContainer), this.top.sync(this.panels.filter((e) => e.top)), this.bottom.sync(this.panels.filter((e) => !e.top));
    for (let e of this.panels) e.dom.classList.add("cm-panel"), e.mount && e.mount();
  }
  update(s45) {
    let t3 = s45.state.facet(fi);
    this.top.container != t3.topContainer && (this.top.sync([]), this.top = new ct(s45.view, true, t3.topContainer)), this.bottom.container != t3.bottomContainer && (this.bottom.sync([]), this.bottom = new ct(s45.view, false, t3.bottomContainer)), this.top.syncClasses(), this.bottom.syncClasses();
    let e = s45.state.facet(ns);
    if (e != this.input) {
      let i2 = e.filter((h) => h), n11 = [], r2 = [], o3 = [], l9 = [];
      for (let h of i2) {
        let a2 = this.specs.indexOf(h), c3;
        a2 < 0 ? (c3 = h(s45.view), l9.push(c3)) : (c3 = this.panels[a2], c3.update && c3.update(s45)), n11.push(c3), (c3.top ? r2 : o3).push(c3);
      }
      this.specs = i2, this.panels = n11, this.top.sync(r2), this.bottom.sync(o3);
      for (let h of l9) h.dom.classList.add("cm-panel"), h.mount && h.mount();
    } else for (let i2 of this.panels) i2.update && i2.update(s45);
  }
  destroy() {
    this.top.sync([]), this.bottom.sync([]);
  }
}, {
  provide: (s45) => M2.scrollMargins.of((t3) => {
    let e = t3.plugin(s45);
    return e && {
      top: e.top.scrollMargin(),
      bottom: e.bottom.scrollMargin()
    };
  })
});
var ct = class {
  constructor(t3, e, i2) {
    this.view = t3, this.top = e, this.container = i2, this.dom = void 0, this.classes = "", this.panels = [], this.syncClasses();
  }
  sync(t3) {
    for (let e of this.panels) e.destroy && t3.indexOf(e) < 0 && e.destroy();
    this.panels = t3, this.syncDOM();
  }
  syncDOM() {
    if (this.panels.length == 0) {
      this.dom && (this.dom.remove(), this.dom = void 0);
      return;
    }
    if (!this.dom) {
      this.dom = document.createElement("div"), this.dom.className = this.top ? "cm-panels cm-panels-top" : "cm-panels cm-panels-bottom", this.dom.style[this.top ? "top" : "bottom"] = "0";
      let e = this.container || this.view.dom;
      e.insertBefore(this.dom, this.top ? e.firstChild : null);
    }
    let t3 = this.dom.firstChild;
    for (let e of this.panels) if (e.dom.parentNode == this.dom) {
      for (; t3 != e.dom; ) t3 = ss(t3);
      t3 = t3.nextSibling;
    } else this.dom.insertBefore(e.dom, t3);
    for (; t3; ) t3 = ss(t3);
  }
  scrollMargin() {
    return !this.dom || this.container ? 0 : Math.max(0, this.top ? this.dom.getBoundingClientRect().bottom - Math.max(0, this.view.scrollDOM.getBoundingClientRect().top) : Math.min(innerHeight, this.view.scrollDOM.getBoundingClientRect().bottom) - this.dom.getBoundingClientRect().top);
  }
  syncClasses() {
    if (!(!this.container || this.classes == this.view.themeClasses)) {
      for (let t3 of this.classes.split(" ")) t3 && this.container.classList.remove(t3);
      for (let t3 of (this.classes = this.view.themeClasses).split(" ")) t3 && this.container.classList.add(t3);
    }
  }
};
function ss(s45) {
  let t3 = s45.nextSibling;
  return s45.remove(), t3;
}
var ns = y.define({
  enables: ln
});
var I2 = class extends z {
  compare(t3) {
    return this == t3 || this.constructor == t3.constructor && this.eq(t3);
  }
  eq(t3) {
    return false;
  }
  destroy(t3) {
  }
};
I2.prototype.elementClass = "";
I2.prototype.toDOM = void 0;
I2.prototype.mapMode = b.TrackBefore;
I2.prototype.startSide = I2.prototype.endSide = -1;
I2.prototype.point = true;
var _t = y.define();
var At = y.define();
var di = y.define({
  combine: (s45) => s45.some((t3) => t3)
});
function hn(s45) {
  let t3 = [
    qr
  ];
  return s45 && s45.fixed === false && t3.push(di.of(true)), t3;
}
var qr = P2.fromClass(class {
  constructor(s45) {
    this.view = s45, this.prevViewport = s45.viewport, this.dom = document.createElement("div"), this.dom.className = "cm-gutters", this.dom.setAttribute("aria-hidden", "true"), this.dom.style.minHeight = this.view.contentHeight + "px", this.gutters = s45.state.facet(At).map((t3) => new pe2(s45, t3));
    for (let t3 of this.gutters) this.dom.appendChild(t3.dom);
    this.fixed = !s45.state.facet(di), this.fixed && (this.dom.style.position = "sticky"), this.syncGutters(false), s45.scrollDOM.insertBefore(this.dom, s45.contentDOM);
  }
  update(s45) {
    if (this.updateGutters(s45)) {
      let t3 = this.prevViewport, e = s45.view.viewport, i2 = Math.min(t3.to, e.to) - Math.max(t3.from, e.from);
      this.syncGutters(i2 < (e.to - e.from) * 0.8);
    }
    s45.geometryChanged && (this.dom.style.minHeight = this.view.contentHeight + "px"), this.view.state.facet(di) != !this.fixed && (this.fixed = !this.fixed, this.dom.style.position = this.fixed ? "sticky" : ""), this.prevViewport = s45.view.viewport;
  }
  syncGutters(s45) {
    let t3 = this.dom.nextSibling;
    s45 && this.dom.remove();
    let e = O.iter(this.view.state.facet(_t), this.view.viewport.from), i2 = [], n11 = this.gutters.map((r2) => new ui(r2, this.view.viewport, -this.view.documentPadding.top));
    for (let r2 of this.view.viewportLineBlocks) {
      let o3;
      if (Array.isArray(r2.type)) {
        for (let l9 of r2.type) if (l9.type == D2.Text) {
          o3 = l9;
          break;
        }
      } else o3 = r2.type == D2.Text ? r2 : void 0;
      if (o3) {
        i2.length && (i2 = []), an(e, i2, r2.from);
        for (let l9 of n11) l9.line(this.view, o3, i2);
      }
    }
    for (let r2 of n11) r2.finish();
    s45 && this.view.scrollDOM.insertBefore(this.dom, t3);
  }
  updateGutters(s45) {
    let t3 = s45.startState.facet(At), e = s45.state.facet(At), i2 = s45.docChanged || s45.heightChanged || s45.viewportChanged || !O.eq(s45.startState.facet(_t), s45.state.facet(_t), s45.view.viewport.from, s45.view.viewport.to);
    if (t3 == e) for (let n11 of this.gutters) n11.update(s45) && (i2 = true);
    else {
      i2 = true;
      let n11 = [];
      for (let r2 of e) {
        let o3 = t3.indexOf(r2);
        o3 < 0 ? n11.push(new pe2(this.view, r2)) : (this.gutters[o3].update(s45), n11.push(this.gutters[o3]));
      }
      for (let r2 of this.gutters) r2.dom.remove(), n11.indexOf(r2) < 0 && r2.destroy();
      for (let r2 of n11) this.dom.appendChild(r2.dom);
      this.gutters = n11;
    }
    return i2;
  }
  destroy() {
    for (let s45 of this.gutters) s45.destroy();
    this.dom.remove();
  }
}, {
  provide: (s45) => M2.scrollMargins.of((t3) => {
    let e = t3.plugin(s45);
    return !e || e.gutters.length == 0 || !e.fixed ? null : t3.textDirection == O2.LTR ? {
      left: e.dom.offsetWidth
    } : {
      right: e.dom.offsetWidth
    };
  })
});
function rs(s45) {
  return Array.isArray(s45) ? s45 : [
    s45
  ];
}
function an(s45, t3, e) {
  for (; s45.value && s45.from <= e; ) s45.from == e && t3.push(s45.value), s45.next();
}
var ui = class {
  constructor(t3, e, i2) {
    this.gutter = t3, this.height = i2, this.localMarkers = [], this.i = 0, this.cursor = O.iter(t3.markers, e.from);
  }
  line(t3, e, i2) {
    this.localMarkers.length && (this.localMarkers = []), an(this.cursor, this.localMarkers, e.from);
    let n11 = i2.length ? this.localMarkers.concat(i2) : this.localMarkers, r2 = this.gutter.config.lineMarker(t3, e, n11);
    r2 && n11.unshift(r2);
    let o3 = this.gutter;
    if (n11.length == 0 && !o3.config.renderEmptyElements) return;
    let l9 = e.top - this.height;
    if (this.i == o3.elements.length) {
      let h = new me2(t3, e.height, l9, n11);
      o3.elements.push(h), o3.dom.appendChild(h.dom);
    } else o3.elements[this.i].update(t3, e.height, l9, n11);
    this.height = e.bottom, this.i++;
  }
  finish() {
    let t3 = this.gutter;
    for (; t3.elements.length > this.i; ) {
      let e = t3.elements.pop();
      t3.dom.removeChild(e.dom), e.destroy();
    }
  }
};
var pe2 = class {
  constructor(t3, e) {
    this.view = t3, this.config = e, this.elements = [], this.spacer = null, this.dom = document.createElement("div"), this.dom.className = "cm-gutter" + (this.config.class ? " " + this.config.class : "");
    for (let i2 in e.domEventHandlers) this.dom.addEventListener(i2, (n11) => {
      let r2 = t3.lineBlockAtHeight(n11.clientY - t3.documentTop);
      e.domEventHandlers[i2](t3, r2, n11) && n11.preventDefault();
    });
    this.markers = rs(e.markers(t3)), e.initialSpacer && (this.spacer = new me2(t3, 0, 0, [
      e.initialSpacer(t3)
    ]), this.dom.appendChild(this.spacer.dom), this.spacer.dom.style.cssText += "visibility: hidden; pointer-events: none");
  }
  update(t3) {
    let e = this.markers;
    if (this.markers = rs(this.config.markers(t3.view)), this.spacer && this.config.updateSpacer) {
      let n11 = this.config.updateSpacer(this.spacer.markers[0], t3);
      n11 != this.spacer.markers[0] && this.spacer.update(t3.view, 0, 0, [
        n11
      ]);
    }
    let i2 = t3.view.viewport;
    return !O.eq(this.markers, e, i2.from, i2.to) || (this.config.lineMarkerChange ? this.config.lineMarkerChange(t3) : false);
  }
  destroy() {
    for (let t3 of this.elements) t3.destroy();
  }
};
var me2 = class {
  constructor(t3, e, i2, n11) {
    this.height = -1, this.above = 0, this.markers = [], this.dom = document.createElement("div"), this.dom.className = "cm-gutterElement", this.update(t3, e, i2, n11);
  }
  update(t3, e, i2, n11) {
    this.height != e && (this.dom.style.height = (this.height = e) + "px"), this.above != i2 && (this.dom.style.marginTop = (this.above = i2) ? i2 + "px" : ""), Kr(this.markers, n11) || this.setMarkers(t3, n11);
  }
  setMarkers(t3, e) {
    let i2 = "cm-gutterElement", n11 = this.dom.firstChild;
    for (let r2 = 0, o3 = 0; ; ) {
      let l9 = o3, h = r2 < e.length ? e[r2++] : null, a2 = false;
      if (h) {
        let c3 = h.elementClass;
        c3 && (i2 += " " + c3);
        for (let f = o3; f < this.markers.length; f++) if (this.markers[f].compare(h)) {
          l9 = f, a2 = true;
          break;
        }
      } else l9 = this.markers.length;
      for (; o3 < l9; ) {
        let c3 = this.markers[o3++];
        if (c3.toDOM) {
          c3.destroy(n11);
          let f = n11.nextSibling;
          n11.remove(), n11 = f;
        }
      }
      if (!h) break;
      h.toDOM && (a2 ? n11 = n11.nextSibling : this.dom.insertBefore(h.toDOM(t3), n11)), a2 && o3++;
    }
    this.dom.className = i2, this.markers = e;
  }
  destroy() {
    this.setMarkers(null, []);
  }
};
function Kr(s45, t3) {
  if (s45.length != t3.length) return false;
  for (let e = 0; e < s45.length; e++) if (!s45[e].compare(t3[e])) return false;
  return true;
}
var jr = y.define();
var ft = y.define({
  combine(s45) {
    return ht(s45, {
      formatNumber: String,
      domEventHandlers: {}
    }, {
      domEventHandlers(t3, e) {
        let i2 = Object.assign({}, t3);
        for (let n11 in e) {
          let r2 = i2[n11], o3 = e[n11];
          i2[n11] = r2 ? (l9, h, a2) => r2(l9, h, a2) || o3(l9, h, a2) : o3;
        }
        return i2;
      }
    });
  }
});
var Dt = class extends I2 {
  constructor(t3) {
    super(), this.number = t3;
  }
  eq(t3) {
    return this.number == t3.number;
  }
  toDOM() {
    return document.createTextNode(this.number);
  }
};
function ke2(s45, t3) {
  return s45.state.facet(ft).formatNumber(t3, s45.state);
}
var Gr = At.compute([
  ft
], (s45) => ({
  class: "cm-lineNumbers",
  renderEmptyElements: false,
  markers(t3) {
    return t3.state.facet(jr);
  },
  lineMarker(t3, e, i2) {
    return i2.some((n11) => n11.toDOM) ? null : new Dt(ke2(t3, t3.state.doc.lineAt(e.from).number));
  },
  lineMarkerChange: (t3) => t3.startState.facet(ft) != t3.state.facet(ft),
  initialSpacer(t3) {
    return new Dt(ke2(t3, os(t3.state.doc.lines)));
  },
  updateSpacer(t3, e) {
    let i2 = ke2(e.view, os(e.view.state.doc.lines));
    return i2 == t3.number ? t3 : new Dt(i2);
  },
  domEventHandlers: s45.facet(ft).domEventHandlers
}));
function go(s45 = {}) {
  return [
    ft.of(s45),
    hn(),
    Gr
  ];
}
function os(s45) {
  let t3 = 9;
  for (; t3 < s45; ) t3 = t3 * 10 + 9;
  return t3;
}
var $r = new class extends I2 {
  constructor() {
    super(...arguments), this.elementClass = "cm-activeLineGutter";
  }
}();
var _r = _t.compute([
  "selection"
], (s45) => {
  let t3 = [], e = -1;
  for (let i2 of s45.selection.ranges) if (i2.empty) {
    let n11 = s45.doc.lineAt(i2.head).from;
    n11 > e && (e = n11, t3.push($r.range(n11)));
  }
  return O.of(t3);
});

// deno:https://esm.sh/@lezer/common@0.16.1/denonext/common.mjs
var Ce3 = 0;
var N3 = class {
  constructor(e, t3) {
    this.from = e, this.to = t3;
  }
};
var w3 = class {
  constructor(e = {}) {
    this.id = Ce3++, this.perNode = !!e.perNode, this.deserialize = e.deserialize || (() => {
      throw new Error("This node type doesn't define a deserialize function");
    });
  }
  add(e) {
    if (this.perNode) throw new RangeError("Can't add per-node props to node types");
    return typeof e != "function" && (e = T4.match(e)), (t3) => {
      let r2 = e(t3);
      return r2 === void 0 ? null : [
        this,
        r2
      ];
    };
  }
};
w3.closedBy = new w3({
  deserialize: (l9) => l9.split(" ")
});
w3.openedBy = new w3({
  deserialize: (l9) => l9.split(" ")
});
w3.group = new w3({
  deserialize: (l9) => l9.split(" ")
});
w3.contextHash = new w3({
  perNode: true
});
w3.lookAhead = new w3({
  perNode: true
});
w3.mounted = new w3({
  perNode: true
});
var _e3 = /* @__PURE__ */ Object.create(null);
var T4 = class l {
  constructor(e, t3, r2, i2 = 0) {
    this.name = e, this.props = t3, this.id = r2, this.flags = i2;
  }
  static define(e) {
    let t3 = e.props && e.props.length ? /* @__PURE__ */ Object.create(null) : _e3, r2 = (e.top ? 1 : 0) | (e.skipped ? 2 : 0) | (e.error ? 4 : 0) | (e.name == null ? 8 : 0), i2 = new l(e.name || "", t3, e.id, r2);
    if (e.props) {
      for (let n11 of e.props) if (Array.isArray(n11) || (n11 = n11(i2)), n11) {
        if (n11[0].perNode) throw new RangeError("Can't store a per-node prop on a node type");
        t3[n11[0].id] = n11[1];
      }
    }
    return i2;
  }
  prop(e) {
    return this.props[e.id];
  }
  get isTop() {
    return (this.flags & 1) > 0;
  }
  get isSkipped() {
    return (this.flags & 2) > 0;
  }
  get isError() {
    return (this.flags & 4) > 0;
  }
  get isAnonymous() {
    return (this.flags & 8) > 0;
  }
  is(e) {
    if (typeof e == "string") {
      if (this.name == e) return true;
      let t3 = this.prop(w3.group);
      return t3 ? t3.indexOf(e) > -1 : false;
    }
    return this.id == e;
  }
  static match(e) {
    let t3 = /* @__PURE__ */ Object.create(null);
    for (let r2 in e) for (let i2 of r2.split(" ")) t3[i2] = e[r2];
    return (r2) => {
      for (let i2 = r2.prop(w3.group), n11 = -1; n11 < (i2 ? i2.length : 0); n11++) {
        let s45 = t3[n11 < 0 ? r2.name : i2[n11]];
        if (s45) return s45;
      }
    };
  }
};
T4.none = new T4("", /* @__PURE__ */ Object.create(null), 0, 8);
var ce3 = class l2 {
  constructor(e) {
    this.types = e;
    for (let t3 = 0; t3 < e.length; t3++) if (e[t3].id != t3) throw new RangeError("Node type ids should correspond to array positions when creating a node set");
  }
  extend(...e) {
    let t3 = [];
    for (let r2 of this.types) {
      let i2 = null;
      for (let n11 of e) {
        let s45 = n11(r2);
        s45 && (i2 || (i2 = Object.assign({}, r2.props)), i2[s45[0].id] = s45[1]);
      }
      t3.push(i2 ? new T4(r2.name, i2, r2.id, r2.flags) : r2);
    }
    return new l2(t3);
  }
};
var K3 = /* @__PURE__ */ new WeakMap();
var ge3 = /* @__PURE__ */ new WeakMap();
var A2;
(function(l9) {
  l9[l9.ExcludeBuffers = 1] = "ExcludeBuffers", l9[l9.IncludeAnonymous = 2] = "IncludeAnonymous", l9[l9.IgnoreMounts = 4] = "IgnoreMounts", l9[l9.IgnoreOverlays = 8] = "IgnoreOverlays";
})(A2 || (A2 = {}));
var z3 = class l3 {
  constructor(e, t3, r2, i2, n11) {
    if (this.type = e, this.children = t3, this.positions = r2, this.length = i2, this.props = null, n11 && n11.length) {
      this.props = /* @__PURE__ */ Object.create(null);
      for (let [s45, h] of n11) this.props[typeof s45 == "number" ? s45 : s45.id] = h;
    }
  }
  toString() {
    let e = this.prop(w3.mounted);
    if (e && !e.overlay) return e.tree.toString();
    let t3 = "";
    for (let r2 of this.children) {
      let i2 = r2.toString();
      i2 && (t3 && (t3 += ","), t3 += i2);
    }
    return this.type.name ? (/\W/.test(this.type.name) && !this.type.isError ? JSON.stringify(this.type.name) : this.type.name) + (t3.length ? "(" + t3 + ")" : "") : t3;
  }
  cursor(e = 0) {
    return new V3(this.topNode, e);
  }
  cursorAt(e, t3 = 0, r2 = 0) {
    let i2 = K3.get(this) || this.topNode, n11 = new V3(i2);
    return n11.moveTo(e, t3), K3.set(this, n11._tree), n11;
  }
  get topNode() {
    return new M3(this, 0, 0, null);
  }
  resolve(e, t3 = 0) {
    let r2 = $2(K3.get(this) || this.topNode, e, t3, false);
    return K3.set(this, r2), r2;
  }
  resolveInner(e, t3 = 0) {
    let r2 = $2(ge3.get(this) || this.topNode, e, t3, true);
    return ge3.set(this, r2), r2;
  }
  iterate(e) {
    let { enter: t3, leave: r2, from: i2 = 0, to: n11 = this.length } = e;
    for (let s45 = this.cursor((e.mode || 0) | A2.IncludeAnonymous); ; ) {
      let h = false;
      if (s45.from <= n11 && s45.to >= i2 && (s45.type.isAnonymous || t3(s45) !== false)) {
        if (s45.firstChild()) continue;
        h = true;
      }
      for (; h && r2 && !s45.type.isAnonymous && r2(s45), !s45.nextSibling(); ) {
        if (!s45.parent()) return;
        h = true;
      }
    }
  }
  prop(e) {
    return e.perNode ? this.props ? this.props[e.id] : void 0 : this.type.prop(e);
  }
  get propValues() {
    let e = [];
    if (this.props) for (let t3 in this.props) e.push([
      +t3,
      this.props[t3]
    ]);
    return e;
  }
  balance(e = {}) {
    return this.children.length <= 8 ? this : ae3(T4.none, this.children, this.positions, 0, this.children.length, 0, this.length, (t3, r2, i2) => new l3(this.type, t3, r2, i2, this.propValues), e.makeTree || ((t3, r2, i2) => new l3(T4.none, t3, r2, i2)));
  }
  static build(e) {
    return Se3(e);
  }
};
z3.empty = new z3(T4.none, [], [], 0);
var ie3 = class l4 {
  constructor(e, t3) {
    this.buffer = e, this.index = t3;
  }
  get id() {
    return this.buffer[this.index - 4];
  }
  get start() {
    return this.buffer[this.index - 3];
  }
  get end() {
    return this.buffer[this.index - 2];
  }
  get size() {
    return this.buffer[this.index - 1];
  }
  get pos() {
    return this.index;
  }
  next() {
    this.index -= 4;
  }
  fork() {
    return new l4(this.buffer, this.index);
  }
};
var W3 = class l5 {
  constructor(e, t3, r2) {
    this.buffer = e, this.length = t3, this.set = r2;
  }
  get type() {
    return T4.none;
  }
  toString() {
    let e = [];
    for (let t3 = 0; t3 < this.buffer.length; ) e.push(this.childString(t3)), t3 = this.buffer[t3 + 3];
    return e.join(",");
  }
  childString(e) {
    let t3 = this.buffer[e], r2 = this.buffer[e + 3], i2 = this.set.types[t3], n11 = i2.name;
    if (/\W/.test(n11) && !i2.isError && (n11 = JSON.stringify(n11)), e += 4, r2 == e) return n11;
    let s45 = [];
    for (; e < r2; ) s45.push(this.childString(e)), e = this.buffer[e + 3];
    return n11 + "(" + s45.join(",") + ")";
  }
  findChild(e, t3, r2, i2, n11) {
    let { buffer: s45 } = this, h = -1;
    for (let f = e; f != t3 && !(ke3(n11, i2, s45[f + 1], s45[f + 2]) && (h = f, r2 > 0)); f = s45[f + 3]) ;
    return h;
  }
  slice(e, t3, r2, i2) {
    let n11 = this.buffer, s45 = new Uint16Array(t3 - e);
    for (let h = e, f = 0; h < t3; ) s45[f++] = n11[h++], s45[f++] = n11[h++] - r2, s45[f++] = n11[h++] - r2, s45[f++] = n11[h++] - e;
    return new l5(s45, i2 - r2, this.set);
  }
};
function ke3(l9, e, t3, r2) {
  switch (l9) {
    case -2:
      return t3 < e;
    case -1:
      return r2 >= e && t3 < e;
    case 0:
      return t3 < e && r2 > e;
    case 1:
      return t3 <= e && r2 > e;
    case 2:
      return r2 > e;
    case 4:
      return true;
  }
}
function Ae2(l9, e) {
  let t3 = l9.childBefore(e);
  for (; t3; ) {
    let r2 = t3.lastChild;
    if (!r2 || r2.to != t3.to) break;
    r2.type.isError && r2.from == r2.to ? (l9 = t3, t3 = r2.prevSibling) : t3 = r2;
  }
  return l9;
}
function $2(l9, e, t3, r2) {
  for (var i2; l9.from == l9.to || (t3 < 1 ? l9.from >= e : l9.from > e) || (t3 > -1 ? l9.to <= e : l9.to < e); ) {
    let s45 = !r2 && l9 instanceof M3 && l9.index < 0 ? null : l9.parent;
    if (!s45) return l9;
    l9 = s45;
  }
  let n11 = r2 ? 0 : A2.IgnoreOverlays;
  if (r2) for (let s45 = l9, h = s45.parent; h; s45 = h, h = s45.parent) s45 instanceof M3 && s45.index < 0 && ((i2 = h.enter(e, t3, n11)) === null || i2 === void 0 ? void 0 : i2.from) != s45.from && (l9 = h);
  for (; ; ) {
    let s45 = l9.enter(e, t3, n11);
    if (!s45) return l9;
    l9 = s45;
  }
}
var M3 = class l6 {
  constructor(e, t3, r2, i2) {
    this._tree = e, this.from = t3, this.index = r2, this._parent = i2;
  }
  get type() {
    return this._tree.type;
  }
  get name() {
    return this._tree.type.name;
  }
  get to() {
    return this.from + this._tree.length;
  }
  nextChild(e, t3, r2, i2, n11 = 0) {
    for (let s45 = this; ; ) {
      for (let { children: h, positions: f } = s45._tree, u2 = t3 > 0 ? h.length : -1; e != u2; e += t3) {
        let o3 = h[e], d = f[e] + s45.from;
        if (ke3(i2, r2, d, d + o3.length)) {
          if (o3 instanceof W3) {
            if (n11 & A2.ExcludeBuffers) continue;
            let a2 = o3.findChild(0, o3.buffer.length, t3, r2 - d, i2);
            if (a2 > -1) return new H2(new ne3(s45, o3, e, d), null, a2);
          } else if (n11 & A2.IncludeAnonymous || !o3.type.isAnonymous || ue3(o3)) {
            let a2;
            if (!(n11 & A2.IgnoreMounts) && o3.props && (a2 = o3.prop(w3.mounted)) && !a2.overlay) return new l6(a2.tree, d, e, s45);
            let y4 = new l6(o3, d, e, s45);
            return n11 & A2.IncludeAnonymous || !y4.type.isAnonymous ? y4 : y4.nextChild(t3 < 0 ? o3.children.length - 1 : 0, t3, r2, i2);
          }
        }
      }
      if (n11 & A2.IncludeAnonymous || !s45.type.isAnonymous || (s45.index >= 0 ? e = s45.index + t3 : e = t3 < 0 ? -1 : s45._parent._tree.children.length, s45 = s45._parent, !s45)) return null;
    }
  }
  get firstChild() {
    return this.nextChild(0, 1, 0, 4);
  }
  get lastChild() {
    return this.nextChild(this._tree.children.length - 1, -1, 0, 4);
  }
  childAfter(e) {
    return this.nextChild(0, 1, e, 2);
  }
  childBefore(e) {
    return this.nextChild(this._tree.children.length - 1, -1, e, -2);
  }
  enter(e, t3, r2 = 0) {
    let i2;
    if (!(r2 & A2.IgnoreOverlays) && (i2 = this._tree.prop(w3.mounted)) && i2.overlay) {
      let n11 = e - this.from;
      for (let { from: s45, to: h } of i2.overlay) if ((t3 > 0 ? s45 <= n11 : s45 < n11) && (t3 < 0 ? h >= n11 : h > n11)) return new l6(i2.tree, i2.overlay[0].from + this.from, -1, this);
    }
    return this.nextChild(0, 1, e, t3, r2);
  }
  nextSignificantParent() {
    let e = this;
    for (; e.type.isAnonymous && e._parent; ) e = e._parent;
    return e;
  }
  get parent() {
    return this._parent ? this._parent.nextSignificantParent() : null;
  }
  get nextSibling() {
    return this._parent && this.index >= 0 ? this._parent.nextChild(this.index + 1, 1, 0, 4) : null;
  }
  get prevSibling() {
    return this._parent && this.index >= 0 ? this._parent.nextChild(this.index - 1, -1, 0, 4) : null;
  }
  cursor(e = 0) {
    return new V3(this, e);
  }
  get tree() {
    return this._tree;
  }
  toTree() {
    return this._tree;
  }
  resolve(e, t3 = 0) {
    return $2(this, e, t3, false);
  }
  resolveInner(e, t3 = 0) {
    return $2(this, e, t3, true);
  }
  enterUnfinishedNodesBefore(e) {
    return Ae2(this, e);
  }
  getChild(e, t3 = null, r2 = null) {
    let i2 = X3(this, e, t3, r2);
    return i2.length ? i2[0] : null;
  }
  getChildren(e, t3 = null, r2 = null) {
    return X3(this, e, t3, r2);
  }
  toString() {
    return this._tree.toString();
  }
  get node() {
    return this;
  }
  matchContext(e) {
    return Y2(this, e);
  }
};
function X3(l9, e, t3, r2) {
  let i2 = l9.cursor(), n11 = [];
  if (!i2.firstChild()) return n11;
  if (t3 != null) {
    for (; !i2.type.is(t3); ) if (!i2.nextSibling()) return n11;
  }
  for (; ; ) {
    if (r2 != null && i2.type.is(r2)) return n11;
    if (i2.type.is(e) && n11.push(i2.node), !i2.nextSibling()) return r2 == null ? n11 : [];
  }
}
function Y2(l9, e, t3 = e.length - 1) {
  for (let r2 = l9.parent; t3 >= 0; r2 = r2.parent) {
    if (!r2) return false;
    if (!r2.type.isAnonymous) {
      if (e[t3] && e[t3] != r2.name) return false;
      t3--;
    }
  }
  return true;
}
var ne3 = class {
  constructor(e, t3, r2, i2) {
    this.parent = e, this.buffer = t3, this.index = r2, this.start = i2;
  }
};
var H2 = class l7 {
  constructor(e, t3, r2) {
    this.context = e, this._parent = t3, this.index = r2, this.type = e.buffer.set.types[e.buffer.buffer[r2]];
  }
  get name() {
    return this.type.name;
  }
  get from() {
    return this.context.start + this.context.buffer.buffer[this.index + 1];
  }
  get to() {
    return this.context.start + this.context.buffer.buffer[this.index + 2];
  }
  child(e, t3, r2) {
    let { buffer: i2 } = this.context, n11 = i2.findChild(this.index + 4, i2.buffer[this.index + 3], e, t3 - this.context.start, r2);
    return n11 < 0 ? null : new l7(this.context, this, n11);
  }
  get firstChild() {
    return this.child(1, 0, 4);
  }
  get lastChild() {
    return this.child(-1, 0, 4);
  }
  childAfter(e) {
    return this.child(1, e, 2);
  }
  childBefore(e) {
    return this.child(-1, e, -2);
  }
  enter(e, t3, r2 = 0) {
    if (r2 & A2.ExcludeBuffers) return null;
    let { buffer: i2 } = this.context, n11 = i2.findChild(this.index + 4, i2.buffer[this.index + 3], t3 > 0 ? 1 : -1, e - this.context.start, t3);
    return n11 < 0 ? null : new l7(this.context, this, n11);
  }
  get parent() {
    return this._parent || this.context.parent.nextSignificantParent();
  }
  externalSibling(e) {
    return this._parent ? null : this.context.parent.nextChild(this.context.index + e, e, 0, 4);
  }
  get nextSibling() {
    let { buffer: e } = this.context, t3 = e.buffer[this.index + 3];
    return t3 < (this._parent ? e.buffer[this._parent.index + 3] : e.buffer.length) ? new l7(this.context, this._parent, t3) : this.externalSibling(1);
  }
  get prevSibling() {
    let { buffer: e } = this.context, t3 = this._parent ? this._parent.index + 4 : 0;
    return this.index == t3 ? this.externalSibling(-1) : new l7(this.context, this._parent, e.findChild(t3, this.index, -1, 0, 4));
  }
  cursor(e = 0) {
    return new V3(this, e);
  }
  get tree() {
    return null;
  }
  toTree() {
    let e = [], t3 = [], { buffer: r2 } = this.context, i2 = this.index + 4, n11 = r2.buffer[this.index + 3];
    if (n11 > i2) {
      let s45 = r2.buffer[this.index + 1], h = r2.buffer[this.index + 2];
      e.push(r2.slice(i2, n11, s45, h)), t3.push(0);
    }
    return new z3(this.type, e, t3, this.to - this.from);
  }
  resolve(e, t3 = 0) {
    return $2(this, e, t3, false);
  }
  resolveInner(e, t3 = 0) {
    return $2(this, e, t3, true);
  }
  enterUnfinishedNodesBefore(e) {
    return Ae2(this, e);
  }
  toString() {
    return this.context.buffer.childString(this.index);
  }
  getChild(e, t3 = null, r2 = null) {
    let i2 = X3(this, e, t3, r2);
    return i2.length ? i2[0] : null;
  }
  getChildren(e, t3 = null, r2 = null) {
    return X3(this, e, t3, r2);
  }
  get node() {
    return this;
  }
  matchContext(e) {
    return Y2(this, e);
  }
};
var V3 = class {
  constructor(e, t3 = 0) {
    if (this.mode = t3, this.buffer = null, this.stack = [], this.index = 0, this.bufferNode = null, e instanceof M3) this.yieldNode(e);
    else {
      this._tree = e.context.parent, this.buffer = e.context;
      for (let r2 = e._parent; r2; r2 = r2._parent) this.stack.unshift(r2.index);
      this.bufferNode = e, this.yieldBuf(e.index);
    }
  }
  get name() {
    return this.type.name;
  }
  yieldNode(e) {
    return e ? (this._tree = e, this.type = e.type, this.from = e.from, this.to = e.to, true) : false;
  }
  yieldBuf(e, t3) {
    this.index = e;
    let { start: r2, buffer: i2 } = this.buffer;
    return this.type = t3 || i2.set.types[i2.buffer[e]], this.from = r2 + i2.buffer[e + 1], this.to = r2 + i2.buffer[e + 2], true;
  }
  yield(e) {
    return e ? e instanceof M3 ? (this.buffer = null, this.yieldNode(e)) : (this.buffer = e.context, this.yieldBuf(e.index, e.type)) : false;
  }
  toString() {
    return this.buffer ? this.buffer.buffer.childString(this.index) : this._tree.toString();
  }
  enterChild(e, t3, r2) {
    if (!this.buffer) return this.yield(this._tree.nextChild(e < 0 ? this._tree._tree.children.length - 1 : 0, e, t3, r2, this.mode));
    let { buffer: i2 } = this.buffer, n11 = i2.findChild(this.index + 4, i2.buffer[this.index + 3], e, t3 - this.buffer.start, r2);
    return n11 < 0 ? false : (this.stack.push(this.index), this.yieldBuf(n11));
  }
  firstChild() {
    return this.enterChild(1, 0, 4);
  }
  lastChild() {
    return this.enterChild(-1, 0, 4);
  }
  childAfter(e) {
    return this.enterChild(1, e, 2);
  }
  childBefore(e) {
    return this.enterChild(-1, e, -2);
  }
  enter(e, t3, r2 = this.mode) {
    return this.buffer ? r2 & A2.ExcludeBuffers ? false : this.enterChild(1, e, t3) : this.yield(this._tree.enter(e, t3, r2));
  }
  parent() {
    if (!this.buffer) return this.yieldNode(this.mode & A2.IncludeAnonymous ? this._tree._parent : this._tree.parent);
    if (this.stack.length) return this.yieldBuf(this.stack.pop());
    let e = this.mode & A2.IncludeAnonymous ? this.buffer.parent : this.buffer.parent.nextSignificantParent();
    return this.buffer = null, this.yieldNode(e);
  }
  sibling(e) {
    if (!this.buffer) return this._tree._parent ? this.yield(this._tree.index < 0 ? null : this._tree._parent.nextChild(this._tree.index + e, e, 0, 4, this.mode)) : false;
    let { buffer: t3 } = this.buffer, r2 = this.stack.length - 1;
    if (e < 0) {
      let i2 = r2 < 0 ? 0 : this.stack[r2] + 4;
      if (this.index != i2) return this.yieldBuf(t3.findChild(i2, this.index, -1, 0, 4));
    } else {
      let i2 = t3.buffer[this.index + 3];
      if (i2 < (r2 < 0 ? t3.buffer.length : t3.buffer[this.stack[r2] + 3])) return this.yieldBuf(i2);
    }
    return r2 < 0 ? this.yield(this.buffer.parent.nextChild(this.buffer.index + e, e, 0, 4, this.mode)) : false;
  }
  nextSibling() {
    return this.sibling(1);
  }
  prevSibling() {
    return this.sibling(-1);
  }
  atLastNode(e) {
    let t3, r2, { buffer: i2 } = this;
    if (i2) {
      if (e > 0) {
        if (this.index < i2.buffer.buffer.length) return false;
      } else for (let n11 = 0; n11 < this.index; n11++) if (i2.buffer.buffer[n11 + 3] < this.index) return false;
      ({ index: t3, parent: r2 } = i2);
    } else ({ index: t3, _parent: r2 } = this._tree);
    for (; r2; { index: t3, _parent: r2 } = r2) if (t3 > -1) for (let n11 = t3 + e, s45 = e < 0 ? -1 : r2._tree.children.length; n11 != s45; n11 += e) {
      let h = r2._tree.children[n11];
      if (this.mode & A2.IncludeAnonymous || h instanceof W3 || !h.type.isAnonymous || ue3(h)) return false;
    }
    return true;
  }
  move(e, t3) {
    if (t3 && this.enterChild(e, 0, 4)) return true;
    for (; ; ) {
      if (this.sibling(e)) return true;
      if (this.atLastNode(e) || !this.parent()) return false;
    }
  }
  next(e = true) {
    return this.move(1, e);
  }
  prev(e = true) {
    return this.move(-1, e);
  }
  moveTo(e, t3 = 0) {
    for (; (this.from == this.to || (t3 < 1 ? this.from >= e : this.from > e) || (t3 > -1 ? this.to <= e : this.to < e)) && this.parent(); ) ;
    for (; this.enterChild(1, e, t3); ) ;
    return this;
  }
  get node() {
    if (!this.buffer) return this._tree;
    let e = this.bufferNode, t3 = null, r2 = 0;
    if (e && e.context == this.buffer) e: for (let i2 = this.index, n11 = this.stack.length; n11 >= 0; ) {
      for (let s45 = e; s45; s45 = s45._parent) if (s45.index == i2) {
        if (i2 == this.index) return s45;
        t3 = s45, r2 = n11 + 1;
        break e;
      }
      i2 = this.stack[--n11];
    }
    for (let i2 = r2; i2 < this.stack.length; i2++) t3 = new H2(this.buffer, t3, this.stack[i2]);
    return this.bufferNode = new H2(this.buffer, t3, this.index);
  }
  get tree() {
    return this.buffer ? null : this._tree._tree;
  }
  iterate(e, t3) {
    for (let r2 = 0; ; ) {
      let i2 = false;
      if (this.type.isAnonymous || e(this) !== false) {
        if (this.firstChild()) {
          r2++;
          continue;
        }
        this.type.isAnonymous || (i2 = true);
      }
      for (; i2 && t3 && t3(this), i2 = this.type.isAnonymous, !this.nextSibling(); ) {
        if (!r2) return;
        this.parent(), r2--, i2 = true;
      }
    }
  }
  matchContext(e) {
    if (!this.buffer) return Y2(this.node, e);
    let { buffer: t3 } = this.buffer, { types: r2 } = t3.set;
    for (let i2 = e.length - 1, n11 = this.stack.length - 1; i2 >= 0; n11--) {
      if (n11 < 0) return Y2(this.node, e, i2);
      let s45 = r2[t3.buffer[this.stack[n11]]];
      if (!s45.isAnonymous) {
        if (e[i2] && e[i2] != s45.name) return false;
        i2--;
      }
    }
    return true;
  }
};
function ue3(l9) {
  return l9.children.some((e) => e instanceof W3 || !e.type.isAnonymous || ue3(e));
}
function Se3(l9) {
  var e;
  let { buffer: t3, nodeSet: r2, maxBufferLength: i2 = 1024, reused: n11 = [], minRepeatType: s45 = r2.types.length } = l9, h = Array.isArray(t3) ? new ie3(t3, t3.length) : t3, f = r2.types, u2 = 0, o3 = 0;
  function d(x5, v3, p2, m4, C6) {
    let { id: b4, start: g3, end: k4, size: B6 } = h, I5 = o3;
    for (; B6 < 0; ) if (h.next(), B6 == -1) {
      let R4 = n11[b4];
      p2.push(R4), m4.push(g3 - x5);
      return;
    } else if (B6 == -3) {
      u2 = b4;
      return;
    } else if (B6 == -4) {
      o3 = b4;
      return;
    } else throw new RangeError(`Unrecognized record size: ${B6}`);
    let G3 = f[b4], L5, F5, pe5 = g3 - x5;
    if (k4 - g3 <= i2 && (F5 = S6(h.pos - v3, C6))) {
      let R4 = new Uint16Array(F5.size - F5.skip), E4 = h.pos - F5.size, D4 = R4.length;
      for (; h.pos > E4; ) D4 = O5(F5.start, R4, D4);
      L5 = new W3(R4, k4 - F5.start, r2), pe5 = F5.start - x5;
    } else {
      let R4 = h.pos - B6;
      h.next();
      let E4 = [], D4 = [], U5 = b4 >= s45 ? b4 : -1, J4 = 0, q4 = k4;
      for (; h.pos > R4; ) U5 >= 0 && h.id == U5 && h.size >= 0 ? (h.end <= q4 - i2 && (y4(E4, D4, g3, J4, h.end, q4, U5, I5), J4 = E4.length, q4 = h.end), h.next()) : d(g3, R4, E4, D4, U5);
      if (U5 >= 0 && J4 > 0 && J4 < E4.length && y4(E4, D4, g3, J4, g3, q4, U5, I5), E4.reverse(), D4.reverse(), U5 > -1 && J4 > 0) {
        let de4 = a2(G3);
        L5 = ae3(G3, E4, D4, 0, E4.length, 0, k4 - g3, de4, de4);
      } else L5 = c3(G3, E4, D4, k4 - g3, I5 - k4);
    }
    p2.push(L5), m4.push(pe5);
  }
  function a2(x5) {
    return (v3, p2, m4) => {
      let C6 = 0, b4 = v3.length - 1, g3, k4;
      if (b4 >= 0 && (g3 = v3[b4]) instanceof z3) {
        if (!b4 && g3.type == x5 && g3.length == m4) return g3;
        (k4 = g3.prop(w3.lookAhead)) && (C6 = p2[b4] + g3.length + k4);
      }
      return c3(x5, v3, p2, m4, C6);
    };
  }
  function y4(x5, v3, p2, m4, C6, b4, g3, k4) {
    let B6 = [], I5 = [];
    for (; x5.length > m4; ) B6.push(x5.pop()), I5.push(v3.pop() + p2 - C6);
    x5.push(c3(r2.types[g3], B6, I5, b4 - C6, k4 - b4)), v3.push(C6 - p2);
  }
  function c3(x5, v3, p2, m4, C6 = 0, b4) {
    if (u2) {
      let g3 = [
        w3.contextHash,
        u2
      ];
      b4 = b4 ? [
        g3
      ].concat(b4) : [
        g3
      ];
    }
    if (C6 > 25) {
      let g3 = [
        w3.lookAhead,
        C6
      ];
      b4 = b4 ? [
        g3
      ].concat(b4) : [
        g3
      ];
    }
    return new z3(x5, v3, p2, m4, b4);
  }
  function S6(x5, v3) {
    let p2 = h.fork(), m4 = 0, C6 = 0, b4 = 0, g3 = p2.end - i2, k4 = {
      size: 0,
      start: 0,
      skip: 0
    };
    e: for (let B6 = p2.pos - x5; p2.pos > B6; ) {
      let I5 = p2.size;
      if (p2.id == v3 && I5 >= 0) {
        k4.size = m4, k4.start = C6, k4.skip = b4, b4 += 4, m4 += 4, p2.next();
        continue;
      }
      let G3 = p2.pos - I5;
      if (I5 < 0 || G3 < B6 || p2.start < g3) break;
      let L5 = p2.id >= s45 ? 4 : 0, F5 = p2.start;
      for (p2.next(); p2.pos > G3; ) {
        if (p2.size < 0) if (p2.size == -3) L5 += 4;
        else break e;
        else p2.id >= s45 && (L5 += 4);
        p2.next();
      }
      C6 = F5, m4 += I5, b4 += L5;
    }
    return (v3 < 0 || m4 == x5) && (k4.size = m4, k4.start = C6, k4.skip = b4), k4.size > 4 ? k4 : void 0;
  }
  function O5(x5, v3, p2) {
    let { id: m4, start: C6, end: b4, size: g3 } = h;
    if (h.next(), g3 >= 0 && m4 < s45) {
      let k4 = p2;
      if (g3 > 4) {
        let B6 = h.pos - (g3 - 4);
        for (; h.pos > B6; ) p2 = O5(x5, v3, p2);
      }
      v3[--p2] = k4, v3[--p2] = b4 - x5, v3[--p2] = C6 - x5, v3[--p2] = m4;
    } else g3 == -3 ? u2 = m4 : g3 == -4 && (o3 = m4);
    return p2;
  }
  let P4 = [], j4 = [];
  for (; h.pos > 0; ) d(l9.start || 0, l9.bufferStart || 0, P4, j4, -1);
  let _5 = (e = l9.length) !== null && e !== void 0 ? e : P4.length ? j4[0] + P4[0].length : 0;
  return new z3(f[l9.topID], P4.reverse(), j4.reverse(), _5);
}
var me3 = /* @__PURE__ */ new WeakMap();
function Q3(l9, e) {
  if (!l9.isAnonymous || e instanceof W3 || e.type != l9) return 1;
  let t3 = me3.get(e);
  if (t3 == null) {
    t3 = 1;
    for (let r2 of e.children) {
      if (r2.type != l9 || !(r2 instanceof z3)) {
        t3 = 1;
        break;
      }
      t3 += Q3(l9, r2);
    }
    me3.set(e, t3);
  }
  return t3;
}
function ae3(l9, e, t3, r2, i2, n11, s45, h, f) {
  let u2 = 0;
  for (let c3 = r2; c3 < i2; c3++) u2 += Q3(l9, e[c3]);
  let o3 = Math.ceil(u2 * 1.5 / 8), d = [], a2 = [];
  function y4(c3, S6, O5, P4, j4) {
    for (let _5 = O5; _5 < P4; ) {
      let x5 = _5, v3 = S6[_5], p2 = Q3(l9, c3[_5]);
      for (_5++; _5 < P4; _5++) {
        let m4 = Q3(l9, c3[_5]);
        if (p2 + m4 >= o3) break;
        p2 += m4;
      }
      if (_5 == x5 + 1) {
        if (p2 > o3) {
          let m4 = c3[x5];
          y4(m4.children, m4.positions, 0, m4.children.length, S6[x5] + j4);
          continue;
        }
        d.push(c3[x5]);
      } else {
        let m4 = S6[_5 - 1] + c3[_5 - 1].length - v3;
        d.push(ae3(l9, c3, S6, x5, _5, v3, m4, null, f));
      }
      a2.push(v3 + j4 - n11);
    }
  }
  return y4(e, t3, r2, i2, 0), (h || f)(d, a2, s45);
}
var Z3 = class l8 {
  constructor(e, t3, r2, i2, n11 = false, s45 = false) {
    this.from = e, this.to = t3, this.tree = r2, this.offset = i2, this.open = (n11 ? 1 : 0) | (s45 ? 2 : 0);
  }
  get openStart() {
    return (this.open & 1) > 0;
  }
  get openEnd() {
    return (this.open & 2) > 0;
  }
  static addTree(e, t3 = [], r2 = false) {
    let i2 = [
      new l8(0, e.length, e, 0, false, r2)
    ];
    for (let n11 of t3) n11.to > e.length && i2.push(n11);
    return i2;
  }
  static applyChanges(e, t3, r2 = 128) {
    if (!t3.length) return e;
    let i2 = [], n11 = 1, s45 = e.length ? e[0] : null;
    for (let h = 0, f = 0, u2 = 0; ; h++) {
      let o3 = h < t3.length ? t3[h] : null, d = o3 ? o3.fromA : 1e9;
      if (d - f >= r2) for (; s45 && s45.from < d; ) {
        let a2 = s45;
        if (f >= a2.from || d <= a2.to || u2) {
          let y4 = Math.max(a2.from, f) - u2, c3 = Math.min(a2.to, d) - u2;
          a2 = y4 >= c3 ? null : new l8(y4, c3, a2.tree, a2.offset + u2, h > 0, !!o3);
        }
        if (a2 && i2.push(a2), s45.to > d) break;
        s45 = n11 < e.length ? e[n11++] : null;
      }
      if (!o3) break;
      f = o3.toA, u2 = o3.toA - o3.toB;
    }
    return i2;
  }
};
var ye3 = class {
  startParse(e, t3, r2) {
    return typeof e == "string" && (e = new se3(e)), r2 = r2 ? r2.length ? r2.map((i2) => new N3(i2.from, i2.to)) : [
      new N3(0, 0)
    ] : [
      new N3(0, e.length)
    ], this.createParse(e, t3 || [], r2);
  }
  parse(e, t3, r2) {
    let i2 = this.startParse(e, t3, r2);
    for (; ; ) {
      let n11 = i2.advance();
      if (n11) return n11;
    }
  }
};
var se3 = class {
  constructor(e) {
    this.string = e;
  }
  get length() {
    return this.string.length;
  }
  chunk(e) {
    return this.string.slice(e);
  }
  get lineChunks() {
    return false;
  }
  read(e, t3) {
    return this.string.slice(e, t3);
  }
};
var he3 = new w3({
  perNode: true
});

// deno:https://esm.sh/@lezer/highlight@0.16.0/denonext/highlight.mjs
var L2 = 0;
var y3 = class o {
  constructor(e, a2, i2) {
    this.set = e, this.base = a2, this.modified = i2, this.id = L2++;
  }
  static define(e) {
    if (e?.base) throw new Error("Can not derive from a modified tag");
    let a2 = new o([], null, []);
    if (a2.set.push(a2), e) for (let i2 of e.set) a2.set.push(i2);
    return a2;
  }
  static defineModifier() {
    let e = new C3();
    return (a2) => a2.modified.indexOf(e) > -1 ? a2 : C3.get(a2.base || a2, a2.modified.concat(e).sort((i2, n11) => i2.id - n11.id));
  }
};
var Q4 = 0;
var C3 = class o2 {
  constructor() {
    this.instances = [], this.id = Q4++;
  }
  static get(e, a2) {
    if (!a2.length) return e;
    let i2 = a2[0].instances.find((r2) => r2.base == e && U3(a2, r2.modified));
    if (i2) return i2;
    let n11 = [], l9 = new y3(n11, e, a2);
    for (let r2 of a2) r2.instances.push(l9);
    let c3 = V4(a2);
    for (let r2 of e.set) for (let p2 of c3) n11.push(o2.get(r2, p2));
    return l9;
  }
};
function U3(o3, e) {
  return o3.length == e.length && o3.every((a2, i2) => a2 == e[i2]);
}
function V4(o3) {
  let e = [
    o3
  ];
  for (let a2 = 0; a2 < o3.length; a2++) for (let i2 of V4(o3.slice(0, a2).concat(o3.slice(a2 + 1)))) e.push(i2);
  return e;
}
function Z4(o3) {
  let e = /* @__PURE__ */ Object.create(null);
  for (let a2 in o3) {
    let i2 = o3[a2];
    Array.isArray(i2) || (i2 = [
      i2
    ]);
    for (let n11 of a2.split(" ")) if (n11) {
      let l9 = [], c3 = 2, r2 = n11;
      for (let m4 = 0; ; ) {
        if (r2 == "..." && m4 > 0 && m4 + 3 == n11.length) {
          c3 = 1;
          break;
        }
        let f = /^"(?:[^"\\]|\\.)*?"|[^\/!]+/.exec(r2);
        if (!f) throw new RangeError("Invalid path: " + n11);
        if (l9.push(f[0] == "*" ? "" : f[0][0] == '"' ? JSON.parse(f[0]) : f[0]), m4 += f[0].length, m4 == n11.length) break;
        let h = n11[m4++];
        if (m4 == n11.length && h == "!") {
          c3 = 0;
          break;
        }
        if (h != "/") throw new RangeError("Invalid path: " + n11);
        r2 = n11.slice(m4);
      }
      let p2 = l9.length - 1, g3 = l9[p2];
      if (!g3) throw new RangeError("Invalid path: " + n11);
      let d = new q3(i2, c3, p2 > 0 ? l9.slice(0, p2) : null);
      e[g3] = d.sort(e[g3]);
    }
  }
  return z4.add(e);
}
var z4 = new w3();
var q3 = class {
  constructor(e, a2, i2, n11) {
    this.tags = e, this.mode = a2, this.context = i2, this.next = n11;
  }
  sort(e) {
    return !e || e.depth < this.depth ? (this.next = e, this) : (e.next = this.sort(e.next), e);
  }
  get depth() {
    return this.context ? this.context.length : 0;
  }
};
function W4(o3, e) {
  let a2 = /* @__PURE__ */ Object.create(null);
  for (let l9 of o3) if (!Array.isArray(l9.tag)) a2[l9.tag.id] = l9.class;
  else for (let c3 of l9.tag) a2[c3.id] = l9.class;
  let { scope: i2, all: n11 = null } = e || {};
  return {
    style: (l9) => {
      let c3 = n11;
      for (let r2 of l9) for (let p2 of r2.set) {
        let g3 = a2[p2.id];
        if (g3) {
          c3 = c3 ? c3 + " " + g3 : g3;
          break;
        }
      }
      return c3;
    },
    scope: i2
  };
}
function X4(o3, e) {
  let a2 = null;
  for (let i2 of o3) {
    let n11 = i2.style(e);
    n11 && (a2 = a2 ? a2 + " " + n11 : n11);
  }
  return a2;
}
function $3(o3, e, a2, i2 = 0, n11 = o3.length) {
  let l9 = new P3(i2, Array.isArray(e) ? e : [
    e
  ], a2);
  l9.highlightRange(o3.cursor(), i2, n11, "", l9.highlighters), l9.flush(n11);
}
var P3 = class {
  constructor(e, a2, i2) {
    this.at = e, this.highlighters = a2, this.span = i2, this.class = "";
  }
  startSpan(e, a2) {
    a2 != this.class && (this.flush(e), e > this.at && (this.at = e), this.class = a2);
  }
  flush(e) {
    e > this.at && this.class && this.span(this.at, e, this.class);
  }
  highlightRange(e, a2, i2, n11, l9) {
    let { type: c3, from: r2, to: p2 } = e;
    if (r2 >= i2 || p2 <= a2) return;
    c3.isTop && (l9 = this.highlighters.filter((h) => !h.scope || h.scope(c3)));
    let g3 = n11, d = c3.prop(z4), m4 = false;
    for (; d; ) {
      if (!d.context || e.matchContext(d.context)) {
        let h = X4(l9, d.tags);
        h && (g3 && (g3 += " "), g3 += h, d.mode == 1 ? n11 += (n11 ? " " : "") + h : d.mode == 0 && (m4 = true));
        break;
      }
      d = d.next;
    }
    if (this.startSpan(e.from, g3), m4) return;
    let f = e.tree && e.tree.prop(w3.mounted);
    if (f && f.overlay) {
      let h = e.node.enter(f.overlay[0].from + r2, 1), G3 = this.highlighters.filter((v3) => !v3.scope || v3.scope(f.tree.type)), D4 = e.firstChild();
      for (let v3 = 0, M6 = r2; ; v3++) {
        let O5 = v3 < f.overlay.length ? f.overlay[v3] : null, T5 = O5 ? O5.from + r2 : p2, H4 = Math.max(a2, M6), E4 = Math.min(i2, T5);
        if (H4 < E4 && D4) for (; e.from < E4 && (this.highlightRange(e, H4, E4, n11, l9), this.startSpan(Math.min(i2, e.to), g3), !(e.to >= T5 || !e.nextSibling())); ) ;
        if (!O5 || T5 > i2) break;
        M6 = O5.to + r2, M6 > a2 && (this.highlightRange(h.cursor(), Math.max(a2, O5.from + r2), Math.min(i2, M6), n11, G3), this.startSpan(M6, g3));
      }
      D4 && e.parent();
    } else if (e.firstChild()) {
      do
        if (!(e.to <= a2)) {
          if (e.from >= i2) break;
          this.highlightRange(e, a2, i2, n11, l9), this.startSpan(Math.min(i2, e.to), g3);
        }
      while (e.nextSibling());
      e.parent();
    }
  }
};
var t2 = y3.define;
var A3 = t2();
var N4 = t2();
var B3 = t2(N4);
var F3 = t2(N4);
var x2 = t2();
var R3 = t2(x2);
var K4 = t2(x2);
var b3 = t2();
var w4 = t2(b3);
var u = t2();
var k2 = t2();
var j2 = t2();
var S3 = t2(j2);
var I3 = t2();
var s44 = {
  comment: A3,
  lineComment: t2(A3),
  blockComment: t2(A3),
  docComment: t2(A3),
  name: N4,
  variableName: t2(N4),
  typeName: B3,
  tagName: t2(B3),
  propertyName: F3,
  attributeName: t2(F3),
  className: t2(N4),
  labelName: t2(N4),
  namespace: t2(N4),
  macroName: t2(N4),
  literal: x2,
  string: R3,
  docString: t2(R3),
  character: t2(R3),
  attributeValue: t2(R3),
  number: K4,
  integer: t2(K4),
  float: t2(K4),
  bool: t2(x2),
  regexp: t2(x2),
  escape: t2(x2),
  color: t2(x2),
  url: t2(x2),
  keyword: u,
  self: t2(u),
  null: t2(u),
  atom: t2(u),
  unit: t2(u),
  modifier: t2(u),
  operatorKeyword: t2(u),
  controlKeyword: t2(u),
  definitionKeyword: t2(u),
  moduleKeyword: t2(u),
  operator: k2,
  derefOperator: t2(k2),
  arithmeticOperator: t2(k2),
  logicOperator: t2(k2),
  bitwiseOperator: t2(k2),
  compareOperator: t2(k2),
  updateOperator: t2(k2),
  definitionOperator: t2(k2),
  typeOperator: t2(k2),
  controlOperator: t2(k2),
  punctuation: j2,
  separator: t2(j2),
  bracket: S3,
  angleBracket: t2(S3),
  squareBracket: t2(S3),
  paren: t2(S3),
  brace: t2(S3),
  content: b3,
  heading: w4,
  heading1: t2(w4),
  heading2: t2(w4),
  heading3: t2(w4),
  heading4: t2(w4),
  heading5: t2(w4),
  heading6: t2(w4),
  contentSeparator: t2(b3),
  list: t2(b3),
  quote: t2(b3),
  emphasis: t2(b3),
  strong: t2(b3),
  link: t2(b3),
  monospace: t2(b3),
  strikethrough: t2(b3),
  inserted: t2(),
  deleted: t2(),
  changed: t2(),
  invalid: t2(),
  meta: I3,
  documentMeta: t2(I3),
  annotation: t2(I3),
  processingInstruction: t2(I3),
  definition: y3.defineModifier(),
  constant: y3.defineModifier(),
  function: y3.defineModifier(),
  standard: y3.defineModifier(),
  local: y3.defineModifier(),
  special: y3.defineModifier()
};
var _2 = W4([
  {
    tag: s44.link,
    class: "tok-link"
  },
  {
    tag: s44.heading,
    class: "tok-heading"
  },
  {
    tag: s44.emphasis,
    class: "tok-emphasis"
  },
  {
    tag: s44.strong,
    class: "tok-strong"
  },
  {
    tag: s44.keyword,
    class: "tok-keyword"
  },
  {
    tag: s44.atom,
    class: "tok-atom"
  },
  {
    tag: s44.bool,
    class: "tok-bool"
  },
  {
    tag: s44.url,
    class: "tok-url"
  },
  {
    tag: s44.labelName,
    class: "tok-labelName"
  },
  {
    tag: s44.inserted,
    class: "tok-inserted"
  },
  {
    tag: s44.deleted,
    class: "tok-deleted"
  },
  {
    tag: s44.literal,
    class: "tok-literal"
  },
  {
    tag: s44.string,
    class: "tok-string"
  },
  {
    tag: s44.number,
    class: "tok-number"
  },
  {
    tag: [
      s44.regexp,
      s44.escape,
      s44.special(s44.string)
    ],
    class: "tok-string2"
  },
  {
    tag: s44.variableName,
    class: "tok-variableName"
  },
  {
    tag: s44.local(s44.variableName),
    class: "tok-variableName tok-local"
  },
  {
    tag: s44.definition(s44.variableName),
    class: "tok-variableName tok-definition"
  },
  {
    tag: s44.special(s44.variableName),
    class: "tok-variableName2"
  },
  {
    tag: s44.definition(s44.propertyName),
    class: "tok-propertyName tok-definition"
  },
  {
    tag: s44.typeName,
    class: "tok-typeName"
  },
  {
    tag: s44.namespace,
    class: "tok-namespace"
  },
  {
    tag: s44.className,
    class: "tok-className"
  },
  {
    tag: s44.macroName,
    class: "tok-macroName"
  },
  {
    tag: s44.propertyName,
    class: "tok-propertyName"
  },
  {
    tag: s44.operator,
    class: "tok-operator"
  },
  {
    tag: s44.comment,
    class: "tok-comment"
  },
  {
    tag: s44.meta,
    class: "tok-meta"
  },
  {
    tag: s44.invalid,
    class: "tok-invalid"
  },
  {
    tag: s44.punctuation,
    class: "tok-punctuation"
  }
]);

// deno:https://esm.sh/@codemirror/language@0.20.2/denonext/language.mjs
var K5;
var C4 = new w3();
function yt2(n11) {
  return y.define({
    combine: n11 ? (t3) => t3.concat(n11) : void 0
  });
}
var c2 = class {
  constructor(t3, e, r2 = []) {
    this.data = t3, I.prototype.hasOwnProperty("tree") || Object.defineProperty(I.prototype, "tree", {
      get() {
        return m3(this);
      }
    }), this.parser = e, this.extension = [
      x3.of(this),
      I.languageData.of((i2, s45, o3) => i2.facet(at3(i2, s45, o3)))
    ].concat(r2);
  }
  isActiveAt(t3, e, r2 = -1) {
    return at3(t3, e, r2) == this.data;
  }
  findRegions(t3) {
    let e = t3.facet(x3);
    if (e?.data == this.data) return [
      {
        from: 0,
        to: t3.doc.length
      }
    ];
    if (!e || !e.allowsNesting) return [];
    let r2 = [], i2 = (s45, o3) => {
      if (s45.prop(C4) == this.data) {
        r2.push({
          from: o3,
          to: o3 + s45.length
        });
        return;
      }
      let a2 = s45.prop(w3.mounted);
      if (a2) {
        if (a2.tree.prop(C4) == this.data) {
          if (a2.overlay) for (let l9 of a2.overlay) r2.push({
            from: l9.from + o3,
            to: l9.to + o3
          });
          else r2.push({
            from: o3,
            to: o3 + s45.length
          });
          return;
        } else if (a2.overlay) {
          let l9 = r2.length;
          if (i2(a2.tree, a2.overlay[0].from + o3), r2.length > l9) return;
        }
      }
      for (let l9 = 0; l9 < s45.children.length; l9++) {
        let h = s45.children[l9];
        h instanceof z3 && i2(h, s45.positions[l9] + o3);
      }
    };
    return i2(m3(t3), 0), r2;
  }
  get allowsNesting() {
    return true;
  }
};
c2.setState = v.define();
function at3(n11, t3, e) {
  let r2 = n11.facet(x3);
  if (!r2) return null;
  let i2 = r2.data;
  if (r2.allowsNesting) for (let s45 = m3(n11).topNode; s45; s45 = s45.enter(t3, e, A2.ExcludeBuffers)) i2 = s45.type.prop(C4) || i2;
  return i2;
}
function m3(n11) {
  let t3 = n11.field(c2.state, false);
  return t3 ? t3.tree : z3.empty;
}
var Y3 = class {
  constructor(t3, e = t3.length) {
    this.doc = t3, this.length = e, this.cursorPos = 0, this.string = "", this.cursor = t3.iter();
  }
  syncTo(t3) {
    return this.string = this.cursor.next(t3 - this.cursorPos).value, this.cursorPos = t3 + this.string.length, this.cursorPos - this.string.length;
  }
  chunk(t3) {
    return this.syncTo(t3), this.string;
  }
  get lineChunks() {
    return true;
  }
  read(t3, e) {
    let r2 = this.cursorPos - this.string.length;
    return t3 < r2 || e >= this.cursorPos ? this.doc.sliceString(t3, e) : this.string.slice(t3 - r2, e - r2);
  }
};
var A4 = null;
var I4 = class n2 {
  constructor(t3, e, r2 = [], i2, s45, o3, a2, l9) {
    this.parser = t3, this.state = e, this.fragments = r2, this.tree = i2, this.treeLen = s45, this.viewport = o3, this.skipped = a2, this.scheduleOn = l9, this.parse = null, this.tempSkipped = [];
  }
  static create(t3, e, r2) {
    return new n2(t3, e, [], z3.empty, 0, r2, [], null);
  }
  startParse() {
    return this.parser.startParse(new Y3(this.state.doc), this.fragments);
  }
  work(t3, e) {
    return e != null && e >= this.state.doc.length && (e = void 0), this.tree != z3.empty && this.isDone(e ?? this.state.doc.length) ? (this.takeTree(), true) : this.withContext(() => {
      var r2;
      if (typeof t3 == "number") {
        let i2 = Date.now() + t3;
        t3 = () => Date.now() > i2;
      }
      for (this.parse || (this.parse = this.startParse()), e != null && (this.parse.stoppedAt == null || this.parse.stoppedAt > e) && e < this.state.doc.length && this.parse.stopAt(e); ; ) {
        let i2 = this.parse.advance();
        if (i2) if (this.fragments = this.withoutTempSkipped(Z3.addTree(i2, this.fragments, this.parse.stoppedAt != null)), this.treeLen = (r2 = this.parse.stoppedAt) !== null && r2 !== void 0 ? r2 : this.state.doc.length, this.tree = i2, this.parse = null, this.treeLen < (e ?? this.state.doc.length)) this.parse = this.startParse();
        else return true;
        if (t3()) return false;
      }
    });
  }
  takeTree() {
    let t3, e;
    this.parse && (t3 = this.parse.parsedPos) >= this.treeLen && ((this.parse.stoppedAt == null || this.parse.stoppedAt > t3) && this.parse.stopAt(t3), this.withContext(() => {
      for (; !(e = this.parse.advance()); ) ;
    }), this.treeLen = t3, this.tree = e, this.fragments = this.withoutTempSkipped(Z3.addTree(this.tree, this.fragments, true)), this.parse = null);
  }
  withContext(t3) {
    let e = A4;
    A4 = this;
    try {
      return t3();
    } finally {
      A4 = e;
    }
  }
  withoutTempSkipped(t3) {
    for (let e; e = this.tempSkipped.pop(); ) t3 = ft2(t3, e.from, e.to);
    return t3;
  }
  changes(t3, e) {
    let { fragments: r2, tree: i2, treeLen: s45, viewport: o3, skipped: a2 } = this;
    if (this.takeTree(), !t3.empty) {
      let l9 = [];
      if (t3.iterChangedRanges((h, u2, d, g3) => l9.push({
        fromA: h,
        toA: u2,
        fromB: d,
        toB: g3
      })), r2 = Z3.applyChanges(r2, l9), i2 = z3.empty, s45 = 0, o3 = {
        from: t3.mapPos(o3.from, -1),
        to: t3.mapPos(o3.to, 1)
      }, this.skipped.length) {
        a2 = [];
        for (let h of this.skipped) {
          let u2 = t3.mapPos(h.from, 1), d = t3.mapPos(h.to, -1);
          u2 < d && a2.push({
            from: u2,
            to: d
          });
        }
      }
    }
    return new n2(this.parser, e, r2, i2, s45, o3, a2, this.scheduleOn);
  }
  updateViewport(t3) {
    if (this.viewport.from == t3.from && this.viewport.to == t3.to) return false;
    this.viewport = t3;
    let e = this.skipped.length;
    for (let r2 = 0; r2 < this.skipped.length; r2++) {
      let { from: i2, to: s45 } = this.skipped[r2];
      i2 < t3.to && s45 > t3.from && (this.fragments = ft2(this.fragments, i2, s45), this.skipped.splice(r2--, 1));
    }
    return this.skipped.length >= e ? false : (this.reset(), true);
  }
  reset() {
    this.parse && (this.takeTree(), this.parse = null);
  }
  skipUntilInView(t3, e) {
    this.skipped.push({
      from: t3,
      to: e
    });
  }
  static getSkippingParser(t3) {
    return new class extends ye3 {
      createParse(e, r2, i2) {
        let s45 = i2[0].from, o3 = i2[i2.length - 1].to;
        return {
          parsedPos: s45,
          advance() {
            let l9 = A4;
            if (l9) {
              for (let h of i2) l9.tempSkipped.push(h);
              t3 && (l9.scheduleOn = l9.scheduleOn ? Promise.all([
                l9.scheduleOn,
                t3
              ]) : t3);
            }
            return this.parsedPos = o3, new z3(T4.none, [], [], o3 - s45);
          },
          stoppedAt: null,
          stopAt() {
          }
        };
      }
    }();
  }
  isDone(t3) {
    t3 = Math.min(t3, this.state.doc.length);
    let e = this.fragments;
    return this.treeLen >= t3 && e.length && e[0].from == 0 && e[0].to >= t3;
  }
  static get() {
    return A4;
  }
};
function ft2(n11, t3, e) {
  return Z3.applyChanges(n11, [
    {
      fromA: t3,
      toA: e,
      fromB: t3,
      toB: e
    }
  ]);
}
var O3 = class n3 {
  constructor(t3) {
    this.context = t3, this.tree = t3.tree;
  }
  apply(t3) {
    if (!t3.docChanged && this.tree == this.context.tree) return this;
    let e = this.context.changes(t3.changes, t3.state), r2 = this.context.treeLen == t3.startState.doc.length ? void 0 : Math.max(t3.changes.mapPos(this.context.treeLen), e.viewport.to);
    return e.work(20, r2) || e.takeTree(), new n3(e);
  }
  static init(t3) {
    let e = Math.min(3e3, t3.doc.length), r2 = I4.create(t3.facet(x3).parser, t3, {
      from: 0,
      to: e
    });
    return r2.work(20, e) || r2.takeTree(), new n3(r2);
  }
};
c2.state = $.define({
  create: O3.init,
  update(n11, t3) {
    for (let e of t3.effects) if (e.is(c2.setState)) return e.value;
    return t3.startState.facet(x3) != t3.state.facet(x3) ? O3.init(t3.state) : n11.apply(t3);
  }
});
var vt2 = (n11) => {
  let t3 = setTimeout(() => n11(), 500);
  return () => clearTimeout(t3);
};
typeof requestIdleCallback < "u" && (vt2 = (n11) => {
  let t3 = -1, e = setTimeout(() => {
    t3 = requestIdleCallback(n11, {
      timeout: 400
    });
  }, 100);
  return () => t3 < 0 ? clearTimeout(e) : cancelIdleCallback(t3);
});
var Q5 = typeof navigator < "u" && (!((K5 = navigator.scheduling) === null || K5 === void 0) && K5.isInputPending) ? () => navigator.scheduling.isInputPending() : null;
var xt2 = P2.fromClass(class {
  constructor(t3) {
    this.view = t3, this.working = null, this.workScheduled = 0, this.chunkEnd = -1, this.chunkBudget = -1, this.work = this.work.bind(this), this.scheduleWork();
  }
  update(t3) {
    let e = this.view.state.field(c2.state).context;
    (e.updateViewport(t3.view.viewport) || this.view.viewport.to > e.treeLen) && this.scheduleWork(), t3.docChanged && (this.view.hasFocus && (this.chunkBudget += 50), this.scheduleWork()), this.checkAsyncSchedule(e);
  }
  scheduleWork() {
    if (this.working) return;
    let { state: t3 } = this.view, e = t3.field(c2.state);
    (e.tree != e.context.tree || !e.context.isDone(t3.doc.length)) && (this.working = vt2(this.work));
  }
  work(t3) {
    this.working = null;
    let e = Date.now();
    if (this.chunkEnd < e && (this.chunkEnd < 0 || this.view.hasFocus) && (this.chunkEnd = e + 3e4, this.chunkBudget = 3e3), this.chunkBudget <= 0) return;
    let { state: r2, viewport: { to: i2 } } = this.view, s45 = r2.field(c2.state);
    if (s45.tree == s45.context.tree && s45.context.isDone(i2 + 1e5)) return;
    let o3 = Date.now() + Math.min(this.chunkBudget, 100, t3 && !Q5 ? Math.max(25, t3.timeRemaining() - 5) : 1e9), a2 = s45.context.treeLen < i2 && r2.doc.length > i2 + 1e3, l9 = s45.context.work(() => Q5 && Q5() || Date.now() > o3, i2 + (a2 ? 0 : 1e5));
    this.chunkBudget -= Date.now() - e, (l9 || this.chunkBudget <= 0) && (s45.context.takeTree(), this.view.dispatch({
      effects: c2.setState.of(new O3(s45.context))
    })), this.chunkBudget > 0 && !(l9 && !a2) && this.scheduleWork(), this.checkAsyncSchedule(s45.context);
  }
  checkAsyncSchedule(t3) {
    t3.scheduleOn && (this.workScheduled++, t3.scheduleOn.then(() => this.scheduleWork()).catch((e) => Z2(this.view.state, e)).then(() => this.workScheduled--), t3.scheduleOn = null);
  }
  destroy() {
    this.working && this.working();
  }
  isWorking() {
    return !!(this.working || this.workScheduled > 0);
  }
}, {
  eventHandlers: {
    focus() {
      this.scheduleWork();
    }
  }
});
var x3 = y.define({
  combine(n11) {
    return n11.length ? n11[0] : null;
  },
  enables: [
    c2.state,
    xt2
  ]
});
var St = y.define();
var Pt2 = y.define({
  combine: (n11) => {
    if (!n11.length) return "  ";
    if (!/^(?: +|\t+)$/.test(n11[0])) throw new Error("Invalid indent unit: " + JSON.stringify(n11[0]));
    return n11[0];
  }
});
function L3(n11) {
  let t3 = n11.facet(Pt2);
  return t3.charCodeAt(0) == 9 ? n11.tabSize * t3.length : t3.length;
}
var ne4 = new w3();
var fe3 = y.define();
var ue4 = new w3();
function Tt2(n11, t3) {
  let e = t3.mapPos(n11.from, 1), r2 = t3.mapPos(n11.to, -1);
  return e >= r2 ? void 0 : {
    from: e,
    to: r2
  };
}
var H3 = v.define({
  map: Tt2
});
var N5 = v.define({
  map: Tt2
});
var S4 = $.define({
  create() {
    return C2.none;
  },
  update(n11, t3) {
    n11 = n11.map(t3.changes);
    for (let e of t3.effects) e.is(H3) && !pe3(n11, e.value.from, e.value.to) ? n11 = n11.update({
      add: [
        ye4.range(e.value.from, e.value.to)
      ]
    }) : e.is(N5) && (n11 = n11.update({
      filter: (r2, i2) => e.value.from != r2 || e.value.to != i2,
      filterFrom: e.value.from,
      filterTo: e.value.to
    }));
    if (t3.selection) {
      let e = false, { head: r2 } = t3.selection.main;
      n11.between(r2, r2, (i2, s45) => {
        i2 < r2 && s45 > r2 && (e = true);
      }), e && (n11 = n11.update({
        filterFrom: r2,
        filterTo: r2,
        filter: (i2, s45) => s45 <= r2 || i2 >= r2
      }));
    }
    return n11;
  },
  provide: (n11) => M2.decorations.from(n11)
});
function W5(n11, t3, e) {
  var r2;
  let i2 = null;
  return (r2 = n11.field(S4, false)) === null || r2 === void 0 || r2.between(t3, e, (s45, o3) => {
    (!i2 || i2.from > s45) && (i2 = {
      from: s45,
      to: o3
    });
  }), i2;
}
function pe3(n11, t3, e) {
  let r2 = false;
  return n11.between(t3, t3, (i2, s45) => {
    i2 == t3 && s45 == e && (r2 = true);
  }), r2;
}
var we3 = {
  placeholderDOM: null,
  placeholderText: "\u2026"
};
var Bt2 = y.define({
  combine(n11) {
    return ht(n11, we3);
  }
});
var ye4 = C2.replace({
  widget: new class extends K2 {
    toDOM(n11) {
      let { state: t3 } = n11, e = t3.facet(Bt2), r2 = (s45) => {
        let o3 = n11.lineBlockAt(n11.posAtDOM(s45.target)), a2 = W5(n11.state, o3.from, o3.to);
        a2 && n11.dispatch({
          effects: N5.of(a2)
        }), s45.preventDefault();
      };
      if (e.placeholderDOM) return e.placeholderDOM(n11, r2);
      let i2 = document.createElement("span");
      return i2.textContent = e.placeholderText, i2.setAttribute("aria-label", t3.phrase("folded code")), i2.title = t3.phrase("unfold"), i2.className = "cm-foldPlaceholder", i2.onclick = r2, i2;
    }
  }()
});
var xe3 = M2.baseTheme({
  ".cm-foldPlaceholder": {
    backgroundColor: "#eee",
    border: "1px solid #ddd",
    color: "#888",
    borderRadius: ".2em",
    margin: "0 1px",
    padding: "0 1px",
    cursor: "pointer"
  },
  ".cm-foldGutter span": {
    padding: "0 1px",
    cursor: "pointer"
  }
});
var j3 = class n4 {
  constructor(t3, e) {
    let r2;
    function i2(a2) {
      let l9 = T2.newName();
      return (r2 || (r2 = /* @__PURE__ */ Object.create(null)))["." + l9] = a2, l9;
    }
    let s45 = typeof e.all == "string" ? e.all : e.all ? i2(e.all) : void 0, o3 = e.scope;
    this.scope = o3 instanceof c2 ? (a2) => a2.prop(C4) == o3.data : o3 ? (a2) => a2 == o3 : void 0, this.style = W4(t3.map((a2) => ({
      tag: a2.tag,
      class: a2.class || i2(Object.assign({}, a2, {
        tag: null
      }))
    })), {
      all: s45
    }).style, this.module = r2 ? new T2(r2) : null, this.themeType = e.themeType;
  }
  static define(t3, e) {
    return new n4(t3, e || {});
  }
};
var _3 = y.define();
var Mt2 = y.define({
  combine(n11) {
    return n11.length ? [
      n11[0]
    ] : null;
  }
});
function F4(n11) {
  let t3 = n11.facet(_3);
  return t3.length ? t3 : n11.facet(Mt2);
}
function en2(n11, t3) {
  let e = [
    Se4
  ], r2;
  return n11 instanceof j3 && (n11.module && e.push(M2.styleModule.of(n11.module)), r2 = n11.themeType), t3?.fallback ? e.push(Mt2.of(n11)) : r2 ? e.push(_3.computeN([
    M2.darkTheme
  ], (i2) => i2.facet(M2.darkTheme) == (r2 == "dark") ? [
    n11
  ] : [])) : e.push(_3.of(n11)), e;
}
var tt3 = class {
  constructor(t3) {
    this.markCache = /* @__PURE__ */ Object.create(null), this.tree = m3(t3.state), this.decorations = this.buildDeco(t3, F4(t3.state));
  }
  update(t3) {
    let e = m3(t3.state), r2 = F4(t3.state), i2 = r2 != F4(t3.startState);
    e.length < t3.view.viewport.to && !i2 && e.type == this.tree.type ? this.decorations = this.decorations.map(t3.changes) : (e != this.tree || t3.viewportChanged || i2) && (this.tree = e, this.decorations = this.buildDeco(t3.view, r2));
  }
  buildDeco(t3, e) {
    if (!e || !this.tree.length) return C2.none;
    let r2 = new se();
    for (let { from: i2, to: s45 } of t3.visibleRanges) $3(this.tree, e, (o3, a2, l9) => {
      r2.add(o3, a2, this.markCache[l9] || (this.markCache[l9] = C2.mark({
        class: l9
      })));
    }, i2, s45);
    return r2.finish();
  }
};
var Se4 = lt.high(P2.fromClass(tt3, {
  decorations: (n11) => n11.decorations
}));
var rn2 = j3.define([
  {
    tag: s44.meta,
    color: "#7a757a"
  },
  {
    tag: s44.link,
    textDecoration: "underline"
  },
  {
    tag: s44.heading,
    textDecoration: "underline",
    fontWeight: "bold"
  },
  {
    tag: s44.emphasis,
    fontStyle: "italic"
  },
  {
    tag: s44.strong,
    fontWeight: "bold"
  },
  {
    tag: s44.strikethrough,
    textDecoration: "line-through"
  },
  {
    tag: s44.keyword,
    color: "#708"
  },
  {
    tag: [
      s44.atom,
      s44.bool,
      s44.url,
      s44.contentSeparator,
      s44.labelName
    ],
    color: "#219"
  },
  {
    tag: [
      s44.literal,
      s44.inserted
    ],
    color: "#164"
  },
  {
    tag: [
      s44.string,
      s44.deleted
    ],
    color: "#a11"
  },
  {
    tag: [
      s44.regexp,
      s44.escape,
      s44.special(s44.string)
    ],
    color: "#e40"
  },
  {
    tag: s44.definition(s44.variableName),
    color: "#00f"
  },
  {
    tag: s44.local(s44.variableName),
    color: "#30a"
  },
  {
    tag: [
      s44.typeName,
      s44.namespace
    ],
    color: "#085"
  },
  {
    tag: s44.className,
    color: "#167"
  },
  {
    tag: [
      s44.special(s44.variableName),
      s44.macroName
    ],
    color: "#256"
  },
  {
    tag: s44.definition(s44.propertyName),
    color: "#00c"
  },
  {
    tag: s44.comment,
    color: "#940"
  },
  {
    tag: s44.invalid,
    color: "#f00"
  }
]);
var Pe3 = M2.baseTheme({
  "&.cm-focused .cm-matchingBracket": {
    backgroundColor: "#328c8252"
  },
  "&.cm-focused .cm-nonmatchingBracket": {
    backgroundColor: "#bb555544"
  }
});
var Et2 = 1e4;
var Ft = "()[]{}";
var Lt2 = y.define({
  combine(n11) {
    return ht(n11, {
      afterCursor: true,
      brackets: Ft,
      maxScanDistance: Et2,
      renderMatch: Te3
    });
  }
});
var Ce4 = C2.mark({
  class: "cm-matchingBracket"
});
var Ae3 = C2.mark({
  class: "cm-nonmatchingBracket"
});
function Te3(n11) {
  let t3 = [], e = n11.matched ? Ce4 : Ae3;
  return t3.push(e.range(n11.start.from, n11.start.to)), n11.end && t3.push(e.range(n11.end.from, n11.end.to)), t3;
}
var De3 = $.define({
  create() {
    return C2.none;
  },
  update(n11, t3) {
    if (!t3.docChanged && !t3.selection) return n11;
    let e = [], r2 = t3.state.facet(Lt2);
    for (let i2 of t3.state.selection.ranges) {
      if (!i2.empty) continue;
      let s45 = M4(t3.state, i2.head, -1, r2) || i2.head > 0 && M4(t3.state, i2.head - 1, 1, r2) || r2.afterCursor && (M4(t3.state, i2.head, 1, r2) || i2.head < t3.state.doc.length && M4(t3.state, i2.head + 1, -1, r2));
      s45 && (e = e.concat(r2.renderMatch(s45, t3.state)));
    }
    return C2.set(e, true);
  },
  provide: (n11) => M2.decorations.from(n11)
});
function et2(n11, t3, e) {
  let r2 = n11.prop(t3 < 0 ? w3.openedBy : w3.closedBy);
  if (r2) return r2;
  if (n11.name.length == 1) {
    let i2 = e.indexOf(n11.name);
    if (i2 > -1 && i2 % 2 == (t3 < 0 ? 1 : 0)) return [
      e[i2 + t3]
    ];
  }
  return null;
}
function M4(n11, t3, e, r2 = {}) {
  let i2 = r2.maxScanDistance || Et2, s45 = r2.brackets || Ft, o3 = m3(n11), a2 = o3.resolveInner(t3, e);
  for (let l9 = a2; l9; l9 = l9.parent) {
    let h = et2(l9.type, e, s45);
    if (h && l9.from < l9.to) return Oe3(n11, t3, e, l9, h, s45);
  }
  return Be3(n11, t3, e, o3, a2.type, i2, s45);
}
function Oe3(n11, t3, e, r2, i2, s45) {
  let o3 = r2.parent, a2 = {
    from: r2.from,
    to: r2.to
  }, l9 = 0, h = o3?.cursor();
  if (h && (e < 0 ? h.childBefore(r2.from) : h.childAfter(r2.to))) do
    if (e < 0 ? h.to <= r2.from : h.from >= r2.to) {
      if (l9 == 0 && i2.indexOf(h.type.name) > -1 && h.from < h.to) return {
        start: a2,
        end: {
          from: h.from,
          to: h.to
        },
        matched: true
      };
      if (et2(h.type, e, s45)) l9++;
      else if (et2(h.type, -e, s45) && (l9--, l9 == 0)) return {
        start: a2,
        end: h.from == h.to ? void 0 : {
          from: h.from,
          to: h.to
        },
        matched: false
      };
    }
  while (e < 0 ? h.prevSibling() : h.nextSibling());
  return {
    start: a2,
    matched: false
  };
}
function Be3(n11, t3, e, r2, i2, s45, o3) {
  let a2 = e < 0 ? n11.sliceDoc(t3 - 1, t3) : n11.sliceDoc(t3, t3 + 1), l9 = o3.indexOf(a2);
  if (l9 < 0 || l9 % 2 == 0 != e > 0) return null;
  let h = {
    from: e < 0 ? t3 - 1 : t3,
    to: e > 0 ? t3 + 1 : t3
  }, u2 = n11.doc.iterRange(t3, e > 0 ? n11.doc.length : 0), d = 0;
  for (let g3 = 0; !u2.next().done && g3 <= s45; ) {
    let b4 = u2.value;
    e < 0 && (g3 += b4.length);
    let q4 = t3 + g3 * e;
    for (let P4 = e > 0 ? 0 : b4.length - 1, $t2 = e > 0 ? b4.length : -1; P4 != $t2; P4 += e) {
      let J4 = o3.indexOf(b4[P4]);
      if (!(J4 < 0 || r2.resolve(q4 + P4, 1).type != i2)) if (J4 % 2 == 0 == e > 0) d++;
      else {
        if (d == 1) return {
          start: h,
          end: {
            from: q4 + P4,
            to: q4 + P4 + 1
          },
          matched: J4 >> 1 == l9 >> 1
        };
        d--;
      }
    }
    e > 0 && (g3 += b4.length);
  }
  return u2.done ? {
    start: h,
    matched: false
  } : null;
}
function dt(n11, t3, e, r2 = 0, i2 = 0) {
  t3 == null && (t3 = n11.search(/[^\s\u00a0]/), t3 == -1 && (t3 = n11.length));
  let s45 = i2;
  for (let o3 = r2; o3 < t3; o3++) n11.charCodeAt(o3) == 9 ? s45 += e - s45 % e : s45++;
  return s45;
}
var $4 = class {
  constructor(t3, e, r2) {
    this.string = t3, this.tabSize = e, this.indentUnit = r2, this.pos = 0, this.start = 0, this.lastColumnPos = 0, this.lastColumnValue = 0;
  }
  eol() {
    return this.pos >= this.string.length;
  }
  sol() {
    return this.pos == 0;
  }
  peek() {
    return this.string.charAt(this.pos) || void 0;
  }
  next() {
    if (this.pos < this.string.length) return this.string.charAt(this.pos++);
  }
  eat(t3) {
    let e = this.string.charAt(this.pos), r2;
    if (typeof t3 == "string" ? r2 = e == t3 : r2 = e && (t3 instanceof RegExp ? t3.test(e) : t3(e)), r2) return ++this.pos, e;
  }
  eatWhile(t3) {
    let e = this.pos;
    for (; this.eat(t3); ) ;
    return this.pos > e;
  }
  eatSpace() {
    let t3 = this.pos;
    for (; /[\s\u00a0]/.test(this.string.charAt(this.pos)); ) ++this.pos;
    return this.pos > t3;
  }
  skipToEnd() {
    this.pos = this.string.length;
  }
  skipTo(t3) {
    let e = this.string.indexOf(t3, this.pos);
    if (e > -1) return this.pos = e, true;
  }
  backUp(t3) {
    this.pos -= t3;
  }
  column() {
    return this.lastColumnPos < this.start && (this.lastColumnValue = dt(this.string, this.start, this.tabSize, this.lastColumnPos, this.lastColumnValue), this.lastColumnPos = this.start), this.lastColumnValue;
  }
  indentation() {
    return dt(this.string, null, this.tabSize);
  }
  match(t3, e, r2) {
    if (typeof t3 == "string") {
      let i2 = (o3) => r2 ? o3.toLowerCase() : o3, s45 = this.string.substr(this.pos, t3.length);
      return i2(s45) == i2(t3) ? (e !== false && (this.pos += t3.length), true) : null;
    } else {
      let i2 = this.string.slice(this.pos).match(t3);
      return i2 && i2.index > 0 ? null : (i2 && e !== false && (this.pos += i2[0].length), i2);
    }
  }
  current() {
    return this.string.slice(this.start, this.pos);
  }
};
function Ne3(n11) {
  return {
    token: n11.token,
    blankLine: n11.blankLine || (() => {
    }),
    startState: n11.startState || (() => true),
    copyState: n11.copyState || Me3,
    indent: n11.indent || (() => null),
    languageData: n11.languageData || {},
    tokenTable: n11.tokenTable || ot3
  };
}
function Me3(n11) {
  if (typeof n11 != "object") return n11;
  let t3 = {};
  for (let e in n11) {
    let r2 = n11[e];
    t3[e] = r2 instanceof Array ? r2.slice() : r2;
  }
  return t3;
}
var pt2 = class n5 extends c2 {
  constructor(t3) {
    let e = yt2(t3.languageData), r2 = Ne3(t3), i2, s45 = new class extends ye3 {
      createParse(o3, a2, l9) {
        return new nt2(i2, o3, a2, l9);
      }
    }();
    super(e, s45, [
      St.of((o3, a2) => this.getIndent(o3, a2))
    ]), this.topNode = Re3(e), i2 = this, this.streamParser = r2, this.stateAfter = new w3({
      perNode: true
    }), this.tokenTable = t3.tokenTable ? new V5(r2.tokenTable) : Le3;
  }
  static define(t3) {
    return new n5(t3);
  }
  getIndent(t3, e) {
    let r2 = m3(t3.state), i2 = r2.resolve(e);
    for (; i2 && i2.type != this.topNode; ) i2 = i2.parent;
    if (!i2) return null;
    let s45 = st2(this, r2, 0, i2.from, e), o3, a2;
    if (s45 ? (a2 = s45.state, o3 = s45.pos + 1) : (a2 = this.streamParser.startState(t3.unit), o3 = 0), e - o3 > 1e4) return null;
    for (; o3 < e; ) {
      let h = t3.state.doc.lineAt(o3), u2 = Math.min(e, h.to);
      if (h.length) {
        let d = new $4(h.text, t3.state.tabSize, t3.unit);
        for (; d.pos < u2 - h.from; ) Ut2(this.streamParser.token, d, a2);
      } else this.streamParser.blankLine(a2, t3.unit);
      if (u2 == e) break;
      o3 = h.to + 1;
    }
    let { text: l9 } = t3.lineAt(e);
    return this.streamParser.indent(a2, /^\s*(.*)/.exec(l9)[1], t3);
  }
  get allowsNesting() {
    return false;
  }
};
function st2(n11, t3, e, r2, i2) {
  let s45 = e >= r2 && e + t3.length <= i2 && t3.prop(n11.stateAfter);
  if (s45) return {
    state: n11.streamParser.copyState(s45),
    pos: e + t3.length
  };
  for (let o3 = t3.children.length - 1; o3 >= 0; o3--) {
    let a2 = t3.children[o3], l9 = e + t3.positions[o3], h = a2 instanceof z3 && l9 < i2 && st2(n11, a2, l9, r2, i2);
    if (h) return h;
  }
  return null;
}
function Rt2(n11, t3, e, r2, i2) {
  if (i2 && e <= 0 && r2 >= t3.length) return t3;
  !i2 && t3.type == n11.topNode && (i2 = true);
  for (let s45 = t3.children.length - 1; s45 >= 0; s45--) {
    let o3 = t3.positions[s45], a2 = t3.children[s45], l9;
    if (o3 < r2 && a2 instanceof z3) {
      if (!(l9 = Rt2(n11, a2, e - o3, r2 - o3, i2))) break;
      return i2 ? new z3(t3.type, t3.children.slice(0, s45).concat(l9), t3.positions.slice(0, s45 + 1), o3 + l9.length) : l9;
    }
  }
  return null;
}
function Ee3(n11, t3, e, r2) {
  for (let i2 of t3) {
    let s45 = i2.from + (i2.openStart ? 25 : 0), o3 = i2.to - (i2.openEnd ? 25 : 0), a2 = s45 <= e && o3 > e && st2(n11, i2.tree, 0 - i2.offset, e, o3), l9;
    if (a2 && (l9 = Rt2(n11, i2.tree, e + i2.offset, a2.pos + i2.offset, false))) return {
      state: a2.state,
      tree: l9
    };
  }
  return {
    state: n11.streamParser.startState(r2 ? L3(r2) : 4),
    tree: z3.empty
  };
}
var nt2 = class {
  constructor(t3, e, r2, i2) {
    this.lang = t3, this.input = e, this.fragments = r2, this.ranges = i2, this.stoppedAt = null, this.chunks = [], this.chunkPos = [], this.chunk = [], this.chunkReused = void 0, this.rangeIndex = 0, this.to = i2[i2.length - 1].to;
    let s45 = I4.get(), o3 = i2[0].from, { state: a2, tree: l9 } = Ee3(t3, r2, o3, s45?.state);
    this.state = a2, this.parsedPos = this.chunkStart = o3 + l9.length;
    for (let h = 0; h < l9.children.length; h++) this.chunks.push(l9.children[h]), this.chunkPos.push(l9.positions[h]);
    s45 && this.parsedPos < s45.viewport.from - 1e5 && (this.state = this.lang.streamParser.startState(L3(s45.state)), s45.skipUntilInView(this.parsedPos, s45.viewport.from), this.parsedPos = s45.viewport.from), this.moveRangeIndex();
  }
  advance() {
    let t3 = I4.get(), e = this.stoppedAt == null ? this.to : Math.min(this.to, this.stoppedAt), r2 = Math.min(e, this.chunkStart + 2048);
    for (t3 && (r2 = Math.min(r2, t3.viewport.to)); this.parsedPos < r2; ) this.parseLine(t3);
    return this.chunkStart < this.parsedPos && this.finishChunk(), this.parsedPos >= e ? this.finish() : t3 && this.parsedPos >= t3.viewport.to ? (t3.skipUntilInView(this.parsedPos, e), this.finish()) : null;
  }
  stopAt(t3) {
    this.stoppedAt = t3;
  }
  lineAfter(t3) {
    let e = this.input.chunk(t3);
    if (this.input.lineChunks) e == `
` && (e = "");
    else {
      let r2 = e.indexOf(`
`);
      r2 > -1 && (e = e.slice(0, r2));
    }
    return t3 + e.length <= this.to ? e : e.slice(0, this.to - t3);
  }
  nextLine() {
    let t3 = this.parsedPos, e = this.lineAfter(t3), r2 = t3 + e.length;
    for (let i2 = this.rangeIndex; ; ) {
      let s45 = this.ranges[i2].to;
      if (s45 >= r2 || (e = e.slice(0, s45 - (r2 - e.length)), i2++, i2 == this.ranges.length)) break;
      let o3 = this.ranges[i2].from, a2 = this.lineAfter(o3);
      e += a2, r2 = o3 + a2.length;
    }
    return {
      line: e,
      end: r2
    };
  }
  skipGapsTo(t3, e, r2) {
    for (; ; ) {
      let i2 = this.ranges[this.rangeIndex].to, s45 = t3 + e;
      if (r2 > 0 ? i2 > s45 : i2 >= s45) break;
      let o3 = this.ranges[++this.rangeIndex].from;
      e += o3 - i2;
    }
    return e;
  }
  moveRangeIndex() {
    for (; this.ranges[this.rangeIndex].to < this.parsedPos; ) this.rangeIndex++;
  }
  emitToken(t3, e, r2, i2, s45) {
    if (this.ranges.length > 1) {
      s45 = this.skipGapsTo(e, s45, 1), e += s45;
      let o3 = this.chunk.length;
      s45 = this.skipGapsTo(r2, s45, -1), r2 += s45, i2 += this.chunk.length - o3;
    }
    return this.chunk.push(t3, e, r2, i2), s45;
  }
  parseLine(t3) {
    let { line: e, end: r2 } = this.nextLine(), i2 = 0, { streamParser: s45 } = this.lang, o3 = new $4(e, t3 ? t3.state.tabSize : 4, t3 ? L3(t3.state) : 2);
    if (o3.eol()) s45.blankLine(this.state, o3.indentUnit);
    else for (; !o3.eol(); ) {
      let a2 = Ut2(s45.token, o3, this.state);
      if (a2 && (i2 = this.emitToken(this.lang.tokenTable.resolve(a2), this.parsedPos + o3.start, this.parsedPos + o3.pos, 4, i2)), o3.start > 1e4) break;
    }
    this.parsedPos = r2, this.moveRangeIndex(), this.parsedPos < this.to && this.parsedPos++;
  }
  finishChunk() {
    let t3 = z3.build({
      buffer: this.chunk,
      start: this.chunkStart,
      length: this.parsedPos - this.chunkStart,
      nodeSet: Fe3,
      topID: 0,
      maxBufferLength: 2048,
      reused: this.chunkReused
    });
    t3 = new z3(t3.type, t3.children, t3.positions, t3.length, [
      [
        this.lang.stateAfter,
        this.lang.streamParser.copyState(this.state)
      ]
    ]), this.chunks.push(t3), this.chunkPos.push(this.chunkStart - this.ranges[0].from), this.chunk = [], this.chunkReused = void 0, this.chunkStart = this.parsedPos;
  }
  finish() {
    return new z3(this.lang.topNode, this.chunks, this.chunkPos, this.parsedPos - this.ranges[0].from).balance();
  }
};
function Ut2(n11, t3, e) {
  t3.start = t3.pos;
  for (let r2 = 0; r2 < 10; r2++) {
    let i2 = n11(t3, e);
    if (t3.pos > t3.start) return i2;
  }
  throw new Error("Stream parser failed to advance stream.");
}
var ot3 = /* @__PURE__ */ Object.create(null);
var B4 = [
  T4.none
];
var Fe3 = new ce3(B4);
var mt = [];
var Wt = /* @__PURE__ */ Object.create(null);
for (let [n11, t3] of [
  [
    "variable",
    "variableName"
  ],
  [
    "variable-2",
    "variableName.special"
  ],
  [
    "string-2",
    "string.special"
  ],
  [
    "def",
    "variableName.definition"
  ],
  [
    "tag",
    "typeName"
  ],
  [
    "attribute",
    "propertyName"
  ],
  [
    "type",
    "typeName"
  ],
  [
    "builtin",
    "variableName.standard"
  ],
  [
    "qualifier",
    "modifier"
  ],
  [
    "error",
    "invalid"
  ],
  [
    "header",
    "heading"
  ],
  [
    "property",
    "propertyName"
  ]
]) Wt[n11] = jt2(ot3, t3);
var V5 = class {
  constructor(t3) {
    this.extra = t3, this.table = Object.assign(/* @__PURE__ */ Object.create(null), Wt);
  }
  resolve(t3) {
    return t3 ? this.table[t3] || (this.table[t3] = jt2(this.extra, t3)) : 0;
  }
};
var Le3 = new V5(ot3);
function X5(n11, t3) {
  mt.indexOf(n11) > -1 || (mt.push(n11), console.warn(t3));
}
function jt2(n11, t3) {
  let e = null;
  for (let s45 of t3.split(".")) {
    let o3 = n11[s45] || s44[s45];
    o3 ? typeof o3 == "function" ? e ? e = o3(e) : X5(s45, `Modifier ${s45} used at start of tag`) : e ? X5(s45, `Tag ${s45} used as modifier`) : e = o3 : X5(s45, `Unknown highlighting tag ${s45}`);
  }
  if (!e) return 0;
  let r2 = t3.replace(/ /g, "_"), i2 = T4.define({
    id: B4.length,
    name: r2,
    props: [
      Z4({
        [r2]: e
      })
    ]
  });
  return B4.push(i2), i2.id;
}
function Re3(n11) {
  let t3 = T4.define({
    id: B4.length,
    name: "Document",
    props: [
      C4.add(() => n11)
    ]
  });
  return B4.push(t3), t3;
}

// deno:https://esm.sh/@codemirror/autocomplete@0.20.3/denonext/autocomplete.mjs
var M5 = class {
  constructor(e, t3, i2) {
    this.state = e, this.pos = t3, this.explicit = i2, this.abortListeners = [];
  }
  tokenBefore(e) {
    let t3 = m3(this.state).resolveInner(this.pos, -1);
    for (; t3 && e.indexOf(t3.name) < 0; ) t3 = t3.parent;
    return t3 ? {
      from: t3.from,
      to: this.pos,
      text: this.state.sliceDoc(t3.from, this.pos),
      type: t3.type
    } : null;
  }
  matchBefore(e) {
    let t3 = this.state.doc.lineAt(this.pos), i2 = Math.max(t3.from, this.pos - 250), o3 = t3.text.slice(i2 - t3.from, this.pos - t3.from), s45 = o3.search(Pe4(e, false));
    return s45 < 0 ? null : {
      from: i2 + s45,
      to: this.pos,
      text: o3.slice(s45)
    };
  }
  get aborted() {
    return this.abortListeners == null;
  }
  addEventListener(e, t3) {
    e == "abort" && this.abortListeners && this.abortListeners.push(t3);
  }
};
function ue5(n11) {
  let e = Object.keys(n11).join(""), t3 = /\w/.test(e);
  return t3 && (e = e.replace(/\w/g, "")), `[${t3 ? "\\w" : ""}${e.replace(/[^\w\s]/g, "\\$&")}]`;
}
function Ye3(n11) {
  let e = /* @__PURE__ */ Object.create(null), t3 = /* @__PURE__ */ Object.create(null);
  for (let { label: o3 } of n11) {
    e[o3[0]] = true;
    for (let s45 = 1; s45 < o3.length; s45++) t3[o3[s45]] = true;
  }
  let i2 = ue5(e) + ue5(t3) + "*$";
  return [
    new RegExp("^" + i2),
    new RegExp(i2)
  ];
}
function Ge3(n11) {
  let e = n11.map((o3) => typeof o3 == "string" ? {
    label: o3
  } : o3), [t3, i2] = e.every((o3) => /^\w+$/.test(o3.label)) ? [
    /\w*$/,
    /\w+$/
  ] : Ye3(e);
  return (o3) => {
    let s45 = o3.matchBefore(i2);
    return s45 || o3.explicit ? {
      from: s45 ? s45.from : o3.pos,
      options: e,
      validFor: t3
    } : null;
  };
}
var B5 = class {
  constructor(e, t3, i2) {
    this.completion = e, this.source = t3, this.match = i2;
  }
};
function x4(n11) {
  return n11.selection.main.head;
}
function Pe4(n11, e) {
  var t3;
  let { source: i2 } = n11, o3 = e && i2[0] != "^", s45 = i2[i2.length - 1] != "$";
  return !o3 && !s45 ? n11 : new RegExp(`${o3 ? "^" : ""}(?:${i2})${s45 ? "$" : ""}`, (t3 = n11.flags) !== null && t3 !== void 0 ? t3 : n11.ignoreCase ? "i" : "");
}
var Ht2 = F.define();
function Je3(n11, e, t3, i2) {
  return Object.assign(Object.assign({}, n11.changeByRange((o3) => {
    if (o3 == n11.selection.main) return {
      changes: {
        from: t3,
        to: i2,
        insert: e
      },
      range: x.cursor(t3 + e.length)
    };
    let s45 = i2 - t3;
    return !o3.empty || s45 && n11.sliceDoc(o3.from - s45, o3.from) != n11.sliceDoc(t3, i2) ? {
      range: o3
    } : {
      changes: {
        from: o3.from - s45,
        to: o3.from,
        insert: e
      },
      range: x.cursor(o3.from - s45 + e.length)
    };
  })), {
    userEvent: "input.complete"
  });
}
function Te4(n11, e) {
  let t3 = e.completion.apply || e.completion.label, i2 = e.source;
  typeof t3 == "string" ? n11.dispatch(Je3(n11.state, t3, i2.from, i2.to)) : t3(n11, e.completion, i2.from, i2.to);
}
var he4 = /* @__PURE__ */ new WeakMap();
function Ze3(n11) {
  if (!Array.isArray(n11)) return n11;
  let e = he4.get(n11);
  return e || he4.set(n11, e = Ge3(n11)), e;
}
var Q6 = class {
  constructor(e) {
    this.pattern = e, this.chars = [], this.folded = [], this.any = [], this.precise = [], this.byWord = [];
    for (let t3 = 0; t3 < e.length; ) {
      let i2 = he(e, t3), o3 = be(i2);
      this.chars.push(i2);
      let s45 = e.slice(t3, t3 + o3), l9 = s45.toUpperCase();
      this.folded.push(he(l9 == s45 ? s45.toLowerCase() : l9, 0)), t3 += o3;
    }
    this.astral = e.length != this.chars.length;
  }
  match(e) {
    if (this.pattern.length == 0) return [
      0
    ];
    if (e.length < this.pattern.length) return null;
    let { chars: t3, folded: i2, any: o3, precise: s45, byWord: l9 } = this;
    if (t3.length == 1) {
      let h = he(e, 0);
      return h == t3[0] ? [
        0,
        0,
        be(h)
      ] : h == i2[0] ? [
        -200,
        0,
        be(h)
      ] : null;
    }
    let r2 = e.indexOf(this.pattern);
    if (r2 == 0) return [
      0,
      0,
      this.pattern.length
    ];
    let c3 = t3.length, a2 = 0;
    if (r2 < 0) {
      for (let h = 0, q4 = Math.min(e.length, 200); h < q4 && a2 < c3; ) {
        let I5 = he(e, h);
        (I5 == t3[a2] || I5 == i2[a2]) && (o3[a2++] = h), h += be(I5);
      }
      if (a2 < c3) return null;
    }
    let f = 0, u2 = 0, $5 = false, w5 = 0, F5 = -1, W6 = -1, $e3 = /[a-z]/.test(e), N6 = true;
    for (let h = 0, q4 = Math.min(e.length, 200), I5 = 0; h < q4 && u2 < c3; ) {
      let d = he(e, h);
      r2 < 0 && (f < c3 && d == t3[f] && (s45[f++] = h), w5 < c3 && (d == t3[w5] || d == i2[w5] ? (w5 == 0 && (F5 = h), W6 = h + 1, w5++) : w5 = 0));
      let R4, H4 = d < 255 ? d >= 48 && d <= 57 || d >= 97 && d <= 122 ? 2 : d >= 65 && d <= 90 ? 1 : 0 : (R4 = rt(d)) != R4.toLowerCase() ? 1 : R4 != R4.toUpperCase() ? 2 : 0;
      (!h || H4 == 1 && $e3 || I5 == 0 && H4 != 0) && (t3[u2] == d || i2[u2] == d && ($5 = true) ? l9[u2++] = h : l9.length && (N6 = false)), I5 = H4, h += be(d);
    }
    return u2 == c3 && l9[0] == 0 && N6 ? this.result(-100 + ($5 ? -200 : 0), l9, e) : w5 == c3 && F5 == 0 ? [
      -200 - e.length,
      0,
      W6
    ] : r2 > -1 ? [
      -700 - e.length,
      r2,
      r2 + this.pattern.length
    ] : w5 == c3 ? [
      -900 - e.length,
      F5,
      W6
    ] : u2 == c3 ? this.result(-100 + ($5 ? -200 : 0) + -700 + (N6 ? 0 : -1100), l9, e) : t3.length == 2 ? null : this.result((o3[0] ? -700 : 0) + -200 + -1100, o3, e);
  }
  result(e, t3, i2) {
    let o3 = [
      e - i2.length
    ], s45 = 1;
    for (let l9 of t3) {
      let r2 = l9 + (this.astral ? be(he(i2, l9)) : 1);
      s45 > 1 && o3[s45 - 1] == l9 ? o3[s45 - 1] = r2 : (o3[s45++] = l9, o3[s45++] = r2);
    }
    return o3;
  }
};
var C5 = y.define({
  combine(n11) {
    return ht(n11, {
      activateOnTyping: true,
      override: null,
      closeOnBlur: true,
      maxRenderedOptions: 100,
      defaultKeymap: true,
      optionClass: () => "",
      aboveCursor: false,
      icons: true,
      addToOptions: []
    }, {
      defaultKeymap: (e, t3) => e && t3,
      closeOnBlur: (e, t3) => e && t3,
      icons: (e, t3) => e && t3,
      optionClass: (e, t3) => (i2) => _e4(e(i2), t3(i2)),
      addToOptions: (e, t3) => e.concat(t3)
    });
  }
});
function _e4(n11, e) {
  return n11 ? e ? n11 + " " + e : n11 : e;
}
function et3(n11) {
  let e = n11.addToOptions.slice();
  return n11.icons && e.push({
    render(t3) {
      let i2 = document.createElement("div");
      return i2.classList.add("cm-completionIcon"), t3.type && i2.classList.add(...t3.type.split(/\s+/g).map((o3) => "cm-completionIcon-" + o3)), i2.setAttribute("aria-hidden", "true"), i2;
    },
    position: 20
  }), e.push({
    render(t3, i2, o3) {
      let s45 = document.createElement("span");
      s45.className = "cm-completionLabel";
      let { label: l9 } = t3, r2 = 0;
      for (let c3 = 1; c3 < o3.length; ) {
        let a2 = o3[c3++], f = o3[c3++];
        a2 > r2 && s45.appendChild(document.createTextNode(l9.slice(r2, a2)));
        let u2 = s45.appendChild(document.createElement("span"));
        u2.appendChild(document.createTextNode(l9.slice(a2, f))), u2.className = "cm-completionMatchedText", r2 = f;
      }
      return r2 < l9.length && s45.appendChild(document.createTextNode(l9.slice(r2))), s45;
    },
    position: 50
  }, {
    render(t3) {
      if (!t3.detail) return null;
      let i2 = document.createElement("span");
      return i2.className = "cm-completionDetail", i2.textContent = t3.detail, i2;
    },
    position: 80
  }), e.sort((t3, i2) => t3.position - i2.position).map((t3) => t3.render);
}
function pe4(n11, e, t3) {
  if (n11 <= t3) return {
    from: 0,
    to: n11
  };
  if (e <= n11 >> 1) {
    let o3 = Math.floor(e / t3);
    return {
      from: o3 * t3,
      to: (o3 + 1) * t3
    };
  }
  let i2 = Math.floor((n11 - e) / t3);
  return {
    from: n11 - (i2 + 1) * t3,
    to: n11 - i2 * t3
  };
}
var X6 = class {
  constructor(e, t3) {
    this.view = e, this.stateField = t3, this.info = null, this.placeInfo = {
      read: () => this.measureInfo(),
      write: (r2) => this.positionInfo(r2),
      key: this
    };
    let i2 = e.state.field(t3), { options: o3, selected: s45 } = i2.open, l9 = e.state.facet(C5);
    this.optionContent = et3(l9), this.optionClass = l9.optionClass, this.range = pe4(o3.length, s45, l9.maxRenderedOptions), this.dom = document.createElement("div"), this.dom.className = "cm-tooltip-autocomplete", this.dom.addEventListener("mousedown", (r2) => {
      for (let c3 = r2.target, a2; c3 && c3 != this.dom; c3 = c3.parentNode) if (c3.nodeName == "LI" && (a2 = /-(\d+)$/.exec(c3.id)) && +a2[1] < o3.length) {
        Te4(e, o3[+a2[1]]), r2.preventDefault();
        return;
      }
    }), this.list = this.dom.appendChild(this.createListBox(o3, i2.id, this.range)), this.list.addEventListener("scroll", () => {
      this.info && this.view.requestMeasure(this.placeInfo);
    });
  }
  mount() {
    this.updateSel();
  }
  update(e) {
    e.state.field(this.stateField) != e.startState.field(this.stateField) && this.updateSel();
  }
  positioned() {
    this.info && this.view.requestMeasure(this.placeInfo);
  }
  updateSel() {
    let e = this.view.state.field(this.stateField), t3 = e.open;
    if ((t3.selected < this.range.from || t3.selected >= this.range.to) && (this.range = pe4(t3.options.length, t3.selected, this.view.state.facet(C5).maxRenderedOptions), this.list.remove(), this.list = this.dom.appendChild(this.createListBox(t3.options, e.id, this.range)), this.list.addEventListener("scroll", () => {
      this.info && this.view.requestMeasure(this.placeInfo);
    })), this.updateSelectedOption(t3.selected)) {
      this.info && (this.info.remove(), this.info = null);
      let { completion: i2 } = t3.options[t3.selected], { info: o3 } = i2;
      if (!o3) return;
      let s45 = typeof o3 == "string" ? document.createTextNode(o3) : o3(i2);
      if (!s45) return;
      "then" in s45 ? s45.then((l9) => {
        l9 && this.view.state.field(this.stateField, false) == e && this.addInfoPane(l9);
      }).catch((l9) => Z2(this.view.state, l9, "completion info")) : this.addInfoPane(s45);
    }
  }
  addInfoPane(e) {
    let t3 = this.info = document.createElement("div");
    t3.className = "cm-tooltip cm-completionInfo", t3.appendChild(e), this.dom.appendChild(t3), this.view.requestMeasure(this.placeInfo);
  }
  updateSelectedOption(e) {
    let t3 = null;
    for (let i2 = this.list.firstChild, o3 = this.range.from; i2; i2 = i2.nextSibling, o3++) o3 == e ? i2.hasAttribute("aria-selected") || (i2.setAttribute("aria-selected", "true"), t3 = i2) : i2.hasAttribute("aria-selected") && i2.removeAttribute("aria-selected");
    return t3 && nt3(this.list, t3), t3;
  }
  measureInfo() {
    let e = this.dom.querySelector("[aria-selected]");
    if (!e || !this.info) return null;
    let t3 = this.dom.getBoundingClientRect(), i2 = this.info.getBoundingClientRect(), o3 = e.getBoundingClientRect();
    if (o3.top > Math.min(innerHeight, t3.bottom) - 10 || o3.bottom < Math.max(0, t3.top) + 10) return null;
    let s45 = Math.max(0, Math.min(o3.top, innerHeight - i2.height)) - t3.top, l9 = this.view.textDirection == O2.RTL, r2 = t3.left, c3 = innerWidth - t3.right;
    return l9 && r2 < Math.min(i2.width, c3) ? l9 = false : !l9 && c3 < Math.min(i2.width, r2) && (l9 = true), {
      top: s45,
      left: l9
    };
  }
  positionInfo(e) {
    this.info && (this.info.style.top = (e ? e.top : -1e6) + "px", e && (this.info.classList.toggle("cm-completionInfo-left", e.left), this.info.classList.toggle("cm-completionInfo-right", !e.left)));
  }
  createListBox(e, t3, i2) {
    let o3 = document.createElement("ul");
    o3.id = t3, o3.setAttribute("role", "listbox"), o3.setAttribute("aria-expanded", "true"), o3.setAttribute("aria-label", this.view.state.phrase("Completions"));
    for (let s45 = i2.from; s45 < i2.to; s45++) {
      let { completion: l9, match: r2 } = e[s45], c3 = o3.appendChild(document.createElement("li"));
      c3.id = t3 + "-" + s45, c3.setAttribute("role", "option");
      let a2 = this.optionClass(l9);
      a2 && (c3.className = a2);
      for (let f of this.optionContent) {
        let u2 = f(l9, this.view.state, r2);
        u2 && c3.appendChild(u2);
      }
    }
    return i2.from && o3.classList.add("cm-completionListIncompleteTop"), i2.to < e.length && o3.classList.add("cm-completionListIncompleteBottom"), o3;
  }
};
function tt4(n11) {
  return (e) => new X6(e, n11);
}
function nt3(n11, e) {
  let t3 = n11.getBoundingClientRect(), i2 = e.getBoundingClientRect();
  i2.top < t3.top ? n11.scrollTop -= t3.top - i2.top : i2.bottom > t3.bottom && (n11.scrollTop += i2.bottom - t3.bottom);
}
function de3(n11) {
  return (n11.boost || 0) * 100 + (n11.apply ? 10 : 0) + (n11.info ? 5 : 0) + (n11.type ? 1 : 0);
}
function it3(n11, e) {
  let t3 = [], i2 = 0;
  for (let l9 of n11) if (l9.hasResult()) if (l9.result.filter === false) {
    let r2 = l9.result.getMatch;
    for (let c3 of l9.result.options) {
      let a2 = [
        1e9 - i2++
      ];
      if (r2) for (let f of r2(c3)) a2.push(f);
      t3.push(new B5(c3, l9, a2));
    }
  } else {
    let r2 = new Q6(e.sliceDoc(l9.from, l9.to)), c3;
    for (let a2 of l9.result.options) (c3 = r2.match(a2.label)) && (a2.boost != null && (c3[0] += a2.boost), t3.push(new B5(a2, l9, c3)));
  }
  let o3 = [], s45 = null;
  for (let l9 of t3.sort(rt3)) !s45 || s45.label != l9.completion.label || s45.detail != l9.completion.detail || s45.type != null && l9.completion.type != null && s45.type != l9.completion.type || s45.apply != l9.completion.apply ? o3.push(l9) : de3(l9.completion) > de3(s45) && (o3[o3.length - 1] = l9), s45 = l9.completion;
  return o3;
}
var Y4 = class n6 {
  constructor(e, t3, i2, o3, s45) {
    this.options = e, this.attrs = t3, this.tooltip = i2, this.timestamp = o3, this.selected = s45;
  }
  setSelected(e, t3) {
    return e == this.selected || e >= this.options.length ? this : new n6(this.options, me4(t3, e), this.tooltip, this.timestamp, e);
  }
  static build(e, t3, i2, o3, s45) {
    let l9 = it3(e, t3);
    if (!l9.length) return null;
    let r2 = 0;
    if (o3 && o3.selected) {
      let c3 = o3.options[o3.selected].completion;
      for (let a2 = 0; a2 < l9.length; a2++) if (l9[a2].completion == c3) {
        r2 = a2;
        break;
      }
    }
    return new n6(l9, me4(i2, r2), {
      pos: e.reduce((c3, a2) => a2.hasResult() ? Math.min(c3, a2.from) : c3, 1e8),
      create: tt4(p),
      above: s45.aboveCursor
    }, o3 ? o3.timestamp : Date.now(), r2);
  }
  map(e) {
    return new n6(this.options, this.attrs, Object.assign(Object.assign({}, this.tooltip), {
      pos: e.mapPos(this.tooltip.pos)
    }), this.timestamp, this.selected);
  }
};
var G2 = class n7 {
  constructor(e, t3, i2) {
    this.active = e, this.id = t3, this.open = i2;
  }
  static start() {
    return new n7(lt2, "cm-ac-" + Math.floor(Math.random() * 2e6).toString(36), null);
  }
  update(e) {
    let { state: t3 } = e, i2 = t3.facet(C5), s45 = (i2.override || t3.languageDataAt("autocomplete", x4(t3)).map(Ze3)).map((r2) => (this.active.find((a2) => a2.source == r2) || new v2(r2, this.active.some((a2) => a2.state != 0) ? 1 : 0)).update(e, i2));
    s45.length == this.active.length && s45.every((r2, c3) => r2 == this.active[c3]) && (s45 = this.active);
    let l9 = e.selection || s45.some((r2) => r2.hasResult() && e.changes.touchesRange(r2.from, r2.to)) || !ot4(s45, this.active) ? Y4.build(s45, t3, this.id, this.open, i2) : this.open && e.docChanged ? this.open.map(e.changes) : this.open;
    !l9 && s45.every((r2) => r2.state != 1) && s45.some((r2) => r2.hasResult()) && (s45 = s45.map((r2) => r2.hasResult() ? new v2(r2.source, 0) : r2));
    for (let r2 of e.effects) r2.is(se4) && (l9 = l9 && l9.setSelected(r2.value, this.id));
    return s45 == this.active && l9 == this.open ? this : new n7(s45, this.id, l9);
  }
  get tooltip() {
    return this.open ? this.open.tooltip : null;
  }
  get attrs() {
    return this.open ? this.open.attrs : st3;
  }
};
function ot4(n11, e) {
  if (n11 == e) return true;
  for (let t3 = 0, i2 = 0; ; ) {
    for (; t3 < n11.length && !n11[t3].hasResult; ) t3++;
    for (; i2 < e.length && !e[i2].hasResult; ) i2++;
    let o3 = t3 == n11.length, s45 = i2 == e.length;
    if (o3 || s45) return o3 == s45;
    if (n11[t3++].result != e[i2++].result) return false;
  }
}
var st3 = {
  "aria-autocomplete": "list"
};
function me4(n11, e) {
  return {
    "aria-autocomplete": "list",
    "aria-haspopup": "listbox",
    "aria-activedescendant": n11 + "-" + e,
    "aria-controls": n11
  };
}
var lt2 = [];
function rt3(n11, e) {
  let t3 = e.match[0] - n11.match[0];
  return t3 || n11.completion.label.localeCompare(e.completion.label);
}
function J3(n11) {
  return n11.isUserEvent("input.type") ? "input" : n11.isUserEvent("delete.backward") ? "delete" : null;
}
var v2 = class n8 {
  constructor(e, t3, i2 = -1) {
    this.source = e, this.state = t3, this.explicitPos = i2;
  }
  hasResult() {
    return false;
  }
  update(e, t3) {
    let i2 = J3(e), o3 = this;
    i2 ? o3 = o3.handleUserEvent(e, i2, t3) : e.docChanged ? o3 = o3.handleChange(e) : e.selection && o3.state != 0 && (o3 = new n8(o3.source, 0));
    for (let s45 of e.effects) if (s45.is(oe3)) o3 = new n8(o3.source, 1, s45.value ? x4(e.state) : -1);
    else if (s45.is(k3)) o3 = new n8(o3.source, 0);
    else if (s45.is(Oe4)) for (let l9 of s45.value) l9.source == o3.source && (o3 = l9);
    return o3;
  }
  handleUserEvent(e, t3, i2) {
    return t3 == "delete" || !i2.activateOnTyping ? this.map(e.changes) : new n8(this.source, 1);
  }
  handleChange(e) {
    return e.changes.touchesRange(x4(e.startState)) ? new n8(this.source, 0) : this.map(e.changes);
  }
  map(e) {
    return e.empty || this.explicitPos < 0 ? this : new n8(this.source, this.state, e.mapPos(this.explicitPos));
  }
};
var Z5 = class n9 extends v2 {
  constructor(e, t3, i2, o3, s45) {
    super(e, 2, t3), this.result = i2, this.from = o3, this.to = s45;
  }
  hasResult() {
    return true;
  }
  handleUserEvent(e, t3, i2) {
    var o3;
    let s45 = e.changes.mapPos(this.from), l9 = e.changes.mapPos(this.to, 1), r2 = x4(e.state);
    if ((this.explicitPos < 0 ? r2 <= s45 : r2 < this.from) || r2 > l9 || t3 == "delete" && x4(e.startState) == this.from) return new v2(this.source, t3 == "input" && i2.activateOnTyping ? 1 : 0);
    let c3 = this.explicitPos < 0 ? -1 : e.changes.mapPos(this.explicitPos), a2;
    return ct2(this.result.validFor, e.state, s45, l9) ? new n9(this.source, c3, this.result, s45, l9) : this.result.update && (a2 = this.result.update(this.result, s45, l9, new M5(e.state, r2, c3 >= 0))) ? new n9(this.source, c3, a2, a2.from, (o3 = a2.to) !== null && o3 !== void 0 ? o3 : x4(e.state)) : new v2(this.source, 1, c3);
  }
  handleChange(e) {
    return e.changes.touchesRange(this.from, this.to) ? new v2(this.source, 0) : this.map(e.changes);
  }
  map(e) {
    return e.empty ? this : new n9(this.source, this.explicitPos < 0 ? -1 : e.mapPos(this.explicitPos), this.result, e.mapPos(this.from), e.mapPos(this.to, 1));
  }
};
function ct2(n11, e, t3, i2) {
  if (!n11) return false;
  let o3 = e.sliceDoc(t3, i2);
  return typeof n11 == "function" ? n11(o3, t3, i2, e) : Pe4(n11, true).test(o3);
}
var oe3 = v.define();
var k3 = v.define();
var Oe4 = v.define({
  map(n11, e) {
    return n11.map((t3) => t3.map(e));
  }
});
var se4 = v.define();
var p = $.define({
  create() {
    return G2.start();
  },
  update(n11, e) {
    return n11.update(e);
  },
  provide: (n11) => [
    rn.from(n11, (e) => e.tooltip),
    M2.contentAttributes.from(n11, (e) => e.attrs)
  ]
});
var Re4 = 75;
function L4(n11, e = "option") {
  return (t3) => {
    let i2 = t3.state.field(p, false);
    if (!i2 || !i2.open || Date.now() - i2.open.timestamp < Re4) return false;
    let o3 = 1, s45;
    e == "page" && (s45 = ho(t3, i2.open.tooltip)) && (o3 = Math.max(2, Math.floor(s45.dom.offsetHeight / s45.dom.querySelector("li").offsetHeight) - 1));
    let l9 = i2.open.selected + o3 * (n11 ? 1 : -1), { length: r2 } = i2.open.options;
    return l9 < 0 ? l9 = e == "page" ? 0 : r2 - 1 : l9 >= r2 && (l9 = e == "page" ? r2 - 1 : 0), t3.dispatch({
      effects: se4.of(l9)
    }), true;
  };
}
var at4 = (n11) => {
  let e = n11.state.field(p, false);
  return n11.state.readOnly || !e || !e.open || Date.now() - e.open.timestamp < Re4 ? false : (Te4(n11, e.open.options[e.open.selected]), true);
};
var ft3 = (n11) => n11.state.field(p, false) ? (n11.dispatch({
  effects: oe3.of(true)
}), true) : false;
var ut = (n11) => {
  let e = n11.state.field(p, false);
  return !e || !e.active.some((t3) => t3.state != 0) ? false : (n11.dispatch({
    effects: k3.of(null)
  }), true);
};
var _4 = class {
  constructor(e, t3) {
    this.active = e, this.context = t3, this.time = Date.now(), this.updates = [], this.done = void 0;
  }
};
var ge4 = 50;
var ht3 = 50;
var pt3 = 1e3;
var dt2 = P2.fromClass(class {
  constructor(n11) {
    this.view = n11, this.debounceUpdate = -1, this.running = [], this.debounceAccept = -1, this.composing = 0;
    for (let e of n11.state.field(p).active) e.state == 1 && this.startQuery(e);
  }
  update(n11) {
    let e = n11.state.field(p);
    if (!n11.selectionSet && !n11.docChanged && n11.startState.field(p) == e) return;
    let t3 = n11.transactions.some((i2) => (i2.selection || i2.docChanged) && !J3(i2));
    for (let i2 = 0; i2 < this.running.length; i2++) {
      let o3 = this.running[i2];
      if (t3 || o3.updates.length + n11.transactions.length > ht3 && Date.now() - o3.time > pt3) {
        for (let s45 of o3.context.abortListeners) try {
          s45();
        } catch (l9) {
          Z2(this.view.state, l9);
        }
        o3.context.abortListeners = null, this.running.splice(i2--, 1);
      } else o3.updates.push(...n11.transactions);
    }
    if (this.debounceUpdate > -1 && clearTimeout(this.debounceUpdate), this.debounceUpdate = e.active.some((i2) => i2.state == 1 && !this.running.some((o3) => o3.active.source == i2.source)) ? setTimeout(() => this.startUpdate(), ge4) : -1, this.composing != 0) for (let i2 of n11.transactions) J3(i2) == "input" ? this.composing = 2 : this.composing == 2 && i2.selection && (this.composing = 3);
  }
  startUpdate() {
    this.debounceUpdate = -1;
    let { state: n11 } = this.view, e = n11.field(p);
    for (let t3 of e.active) t3.state == 1 && !this.running.some((i2) => i2.active.source == t3.source) && this.startQuery(t3);
  }
  startQuery(n11) {
    let { state: e } = this.view, t3 = x4(e), i2 = new M5(e, t3, n11.explicitPos == t3), o3 = new _4(n11, i2);
    this.running.push(o3), Promise.resolve(n11.source(i2)).then((s45) => {
      o3.context.aborted || (o3.done = s45 || null, this.scheduleAccept());
    }, (s45) => {
      this.view.dispatch({
        effects: k3.of(null)
      }), Z2(this.view.state, s45);
    });
  }
  scheduleAccept() {
    this.running.every((n11) => n11.done !== void 0) ? this.accept() : this.debounceAccept < 0 && (this.debounceAccept = setTimeout(() => this.accept(), ge4));
  }
  accept() {
    var n11;
    this.debounceAccept > -1 && clearTimeout(this.debounceAccept), this.debounceAccept = -1;
    let e = [], t3 = this.view.state.facet(C5);
    for (let i2 = 0; i2 < this.running.length; i2++) {
      let o3 = this.running[i2];
      if (o3.done === void 0) continue;
      if (this.running.splice(i2--, 1), o3.done) {
        let l9 = new Z5(o3.active.source, o3.active.explicitPos, o3.done, o3.done.from, (n11 = o3.done.to) !== null && n11 !== void 0 ? n11 : x4(o3.updates.length ? o3.updates[0].startState : this.view.state));
        for (let r2 of o3.updates) l9 = l9.update(r2, t3);
        if (l9.hasResult()) {
          e.push(l9);
          continue;
        }
      }
      let s45 = this.view.state.field(p).active.find((l9) => l9.source == o3.active.source);
      if (s45 && s45.state == 1) if (o3.done == null) {
        let l9 = new v2(o3.active.source, 0);
        for (let r2 of o3.updates) l9 = l9.update(r2, t3);
        l9.state != 1 && e.push(l9);
      } else this.startQuery(s45);
    }
    e.length && this.view.dispatch({
      effects: Oe4.of(e)
    });
  }
}, {
  eventHandlers: {
    blur() {
      let n11 = this.view.state.field(p, false);
      n11 && n11.tooltip && this.view.state.facet(C5).closeOnBlur && this.view.dispatch({
        effects: k3.of(null)
      });
    },
    compositionstart() {
      this.composing = 1;
    },
    compositionend() {
      this.composing == 3 && setTimeout(() => this.view.dispatch({
        effects: oe3.of(false)
      }), 20), this.composing = 0;
    }
  }
});
var Le4 = M2.baseTheme({
  ".cm-tooltip.cm-tooltip-autocomplete": {
    "& > ul": {
      fontFamily: "monospace",
      whiteSpace: "nowrap",
      overflow: "hidden auto",
      maxWidth_fallback: "700px",
      maxWidth: "min(700px, 95vw)",
      minWidth: "250px",
      maxHeight: "10em",
      listStyle: "none",
      margin: 0,
      padding: 0,
      "& > li": {
        overflowX: "hidden",
        textOverflow: "ellipsis",
        cursor: "pointer",
        padding: "1px 3px",
        lineHeight: 1.2
      }
    }
  },
  "&light .cm-tooltip-autocomplete ul li[aria-selected]": {
    background: "#17c",
    color: "white"
  },
  "&dark .cm-tooltip-autocomplete ul li[aria-selected]": {
    background: "#347",
    color: "white"
  },
  ".cm-completionListIncompleteTop:before, .cm-completionListIncompleteBottom:after": {
    content: '"\xB7\xB7\xB7"',
    opacity: 0.5,
    display: "block",
    textAlign: "center"
  },
  ".cm-tooltip.cm-completionInfo": {
    position: "absolute",
    padding: "3px 9px",
    width: "max-content",
    maxWidth: "300px"
  },
  ".cm-completionInfo.cm-completionInfo-left": {
    right: "100%"
  },
  ".cm-completionInfo.cm-completionInfo-right": {
    left: "100%"
  },
  "&light .cm-snippetField": {
    backgroundColor: "#00000022"
  },
  "&dark .cm-snippetField": {
    backgroundColor: "#ffffff22"
  },
  ".cm-snippetFieldPosition": {
    verticalAlign: "text-top",
    width: 0,
    height: "1.15em",
    margin: "0 -0.7px -.7em",
    borderLeft: "1.4px dotted #888"
  },
  ".cm-completionMatchedText": {
    textDecoration: "underline"
  },
  ".cm-completionDetail": {
    marginLeft: "0.5em",
    fontStyle: "italic"
  },
  ".cm-completionIcon": {
    fontSize: "90%",
    width: ".8em",
    display: "inline-block",
    textAlign: "center",
    paddingRight: ".6em",
    opacity: "0.6"
  },
  ".cm-completionIcon-function, .cm-completionIcon-method": {
    "&:after": {
      content: "'\u0192'"
    }
  },
  ".cm-completionIcon-class": {
    "&:after": {
      content: "'\u25CB'"
    }
  },
  ".cm-completionIcon-interface": {
    "&:after": {
      content: "'\u25CC'"
    }
  },
  ".cm-completionIcon-variable": {
    "&:after": {
      content: "'\u{1D465}'"
    }
  },
  ".cm-completionIcon-constant": {
    "&:after": {
      content: "'\u{1D436}'"
    }
  },
  ".cm-completionIcon-type": {
    "&:after": {
      content: "'\u{1D461}'"
    }
  },
  ".cm-completionIcon-enum": {
    "&:after": {
      content: "'\u222A'"
    }
  },
  ".cm-completionIcon-property": {
    "&:after": {
      content: "'\u25A1'"
    }
  },
  ".cm-completionIcon-keyword": {
    "&:after": {
      content: "'\u{1F511}\uFE0E'"
    }
  },
  ".cm-completionIcon-namespace": {
    "&:after": {
      content: "'\u25A2'"
    }
  },
  ".cm-completionIcon-text": {
    "&:after": {
      content: "'abc'",
      fontSize: "50%",
      verticalAlign: "middle"
    }
  }
});
var mt2 = C2.widget({
  widget: new class extends K2 {
    toDOM() {
      let n11 = document.createElement("span");
      return n11.className = "cm-snippetFieldPosition", n11;
    }
    ignoreEvent() {
      return false;
    }
  }()
});
var gt = C2.mark({
  class: "cm-snippetField"
});
var A5 = class n10 {
  constructor(e, t3) {
    this.ranges = e, this.active = t3, this.deco = C2.set(e.map((i2) => (i2.from == i2.to ? mt2 : gt).range(i2.from, i2.to)));
  }
  map(e) {
    let t3 = [];
    for (let i2 of this.ranges) {
      let o3 = i2.map(e);
      if (!o3) return null;
      t3.push(o3);
    }
    return new n10(t3, this.active);
  }
  selectionInsideField(e) {
    return e.ranges.every((t3) => this.ranges.some((i2) => i2.field == this.active && i2.from <= t3.from && i2.to >= t3.to));
  }
};
var O4 = v.define({
  map(n11, e) {
    return n11 && n11.map(e);
  }
});
var bt2 = v.define();
var E3 = $.define({
  create() {
    return null;
  },
  update(n11, e) {
    for (let t3 of e.effects) {
      if (t3.is(O4)) return t3.value;
      if (t3.is(bt2) && n11) return new A5(n11.ranges, t3.value);
    }
    return n11 && e.docChanged && (n11 = n11.map(e.changes)), n11 && e.selection && !n11.selectionInsideField(e.selection) && (n11 = null), n11;
  },
  provide: (n11) => M2.decorations.from(n11, (e) => e ? e.deco : C2.none)
});
function le2(n11, e) {
  return x.create(n11.filter((t3) => t3.field == e).map((t3) => x.range(t3.from, t3.to)));
}
function Me4(n11) {
  return ({ state: e, dispatch: t3 }) => {
    let i2 = e.field(E3, false);
    if (!i2 || n11 < 0 && i2.active == 0) return false;
    let o3 = i2.active + n11, s45 = n11 > 0 && !i2.ranges.some((l9) => l9.field == o3 + n11);
    return t3(e.update({
      selection: le2(i2.ranges, o3),
      effects: O4.of(s45 ? null : new A5(i2.ranges, o3))
    })), true;
  };
}
var yt3 = ({ state: n11, dispatch: e }) => n11.field(E3, false) ? (e(n11.update({
  effects: O4.of(null)
})), true) : false;
var wt2 = Me4(1);
var xt3 = Me4(-1);
var Ct2 = [
  {
    key: "Tab",
    run: wt2,
    shift: xt3
  },
  {
    key: "Escape",
    run: yt3
  }
];
var be3 = y.define({
  combine(n11) {
    return n11.length ? n11[0] : Ct2;
  }
});
var St2 = lt.highest(ur.compute([
  be3
], (n11) => n11.facet(be3)));
var It2 = M2.domEventHandlers({
  mousedown(n11, e) {
    let t3 = e.state.field(E3, false), i2;
    if (!t3 || (i2 = e.posAtCoords({
      x: n11.clientX,
      y: n11.clientY
    })) == null) return false;
    let o3 = t3.ranges.find((s45) => s45.from <= i2 && s45.to >= i2);
    return !o3 || o3.field == t3.active ? false : (e.dispatch({
      selection: le2(t3.ranges, o3.field),
      effects: O4.of(t3.ranges.some((s45) => s45.field > o3.field) ? new A5(t3.ranges, o3.field) : null)
    }), true);
  }
});
var D3 = {
  brackets: [
    "(",
    "[",
    "{",
    "'",
    '"'
  ],
  before: ")]}:;>"
};
var S5 = v.define({
  map(n11, e) {
    let t3 = e.mapPos(n11, -1, b.TrackAfter);
    return t3 ?? void 0;
  }
});
var re3 = v.define({
  map(n11, e) {
    return e.mapPos(n11);
  }
});
var ce4 = new class extends z {
}();
ce4.startSide = 1;
ce4.endSide = -1;
var ke4 = $.define({
  create() {
    return O.empty;
  },
  update(n11, e) {
    if (e.selection) {
      let t3 = e.state.doc.lineAt(e.selection.main.head).from, i2 = e.startState.doc.lineAt(e.startState.selection.main.head).from;
      t3 != e.changes.mapPos(i2, -1) && (n11 = O.empty);
    }
    n11 = n11.map(e.changes);
    for (let t3 of e.effects) t3.is(S5) ? n11 = n11.update({
      add: [
        ce4.range(t3.value, t3.value + 1)
      ]
    }) : t3.is(re3) && (n11 = n11.update({
      filter: (i2) => i2 != t3.value
    }));
    return n11;
  }
});
var V6 = "()[]{}<>";
function De4(n11) {
  for (let e = 0; e < V6.length; e += 2) if (V6.charCodeAt(e) == n11) return V6.charAt(e + 1);
  return rt(n11 < 128 ? n11 : n11 + 1);
}
function je3(n11, e) {
  return n11.languageDataAt("closeBrackets", e)[0] || D3;
}
var Pt3 = typeof navigator == "object" && /Android\b/.test(navigator.userAgent);
var Tt3 = M2.inputHandler.of((n11, e, t3, i2) => {
  if ((Pt3 ? n11.composing : n11.compositionStarted) || n11.state.readOnly) return false;
  let o3 = n11.state.selection.main;
  if (i2.length > 2 || i2.length == 2 && be(he(i2, 0)) == 1 || e != o3.from || t3 != o3.to) return false;
  let s45 = Rt3(n11.state, i2);
  return s45 ? (n11.dispatch(s45), true) : false;
});
function Rt3(n11, e) {
  let t3 = je3(n11, n11.selection.main.head), i2 = t3.brackets || D3.brackets;
  for (let o3 of i2) {
    let s45 = De4(he(o3, 0));
    if (e == o3) return s45 == o3 ? kt2(n11, o3, i2.indexOf(o3 + o3 + o3) > -1) : Mt3(n11, o3, s45, t3.before || D3.before);
    if (e == s45 && Ue3(n11, n11.selection.main.from)) return Bt3(n11, o3, s45);
  }
  return null;
}
function Ue3(n11, e) {
  let t3 = false;
  return n11.field(ke4).between(0, n11.doc.length, (i2) => {
    i2 == e && (t3 = true);
  }), t3;
}
function U4(n11, e) {
  let t3 = n11.sliceString(e, e + 2);
  return t3.slice(0, be(he(t3, 0)));
}
function Mt3(n11, e, t3, i2) {
  let o3 = null, s45 = n11.changeByRange((l9) => {
    if (!l9.empty) return {
      changes: [
        {
          insert: e,
          from: l9.from
        },
        {
          insert: t3,
          from: l9.to
        }
      ],
      effects: S5.of(l9.to + e.length),
      range: x.range(l9.anchor + e.length, l9.head + e.length)
    };
    let r2 = U4(n11.doc, l9.head);
    return !r2 || /\s/.test(r2) || i2.indexOf(r2) > -1 ? {
      changes: {
        insert: e + t3,
        from: l9.head
      },
      effects: S5.of(l9.head + e.length),
      range: x.cursor(l9.head + e.length)
    } : {
      range: o3 = l9
    };
  });
  return o3 ? null : n11.update(s45, {
    scrollIntoView: true,
    userEvent: "input.type"
  });
}
function Bt3(n11, e, t3) {
  let i2 = null, o3 = n11.selection.ranges.map((s45) => s45.empty && U4(n11.doc, s45.head) == t3 ? x.cursor(s45.head + t3.length) : i2 = s45);
  return i2 ? null : n11.update({
    selection: x.create(o3, n11.selection.mainIndex),
    scrollIntoView: true,
    effects: n11.selection.ranges.map(({ from: s45 }) => re3.of(s45))
  });
}
function kt2(n11, e, t3) {
  let i2 = null, o3 = n11.changeByRange((s45) => {
    if (!s45.empty) return {
      changes: [
        {
          insert: e,
          from: s45.from
        },
        {
          insert: e,
          from: s45.to
        }
      ],
      effects: S5.of(s45.to + e.length),
      range: x.range(s45.anchor + e.length, s45.head + e.length)
    };
    let l9 = s45.head, r2 = U4(n11.doc, l9);
    if (r2 == e) {
      if (xe4(n11, l9)) return {
        changes: {
          insert: e + e,
          from: l9
        },
        effects: S5.of(l9 + e.length),
        range: x.cursor(l9 + e.length)
      };
      if (Ue3(n11, l9)) {
        let c3 = t3 && n11.sliceDoc(l9, l9 + e.length * 3) == e + e + e;
        return {
          range: x.cursor(l9 + e.length * (c3 ? 3 : 1)),
          effects: re3.of(l9)
        };
      }
    } else {
      if (t3 && n11.sliceDoc(l9 - 2 * e.length, l9) == e + e && xe4(n11, l9 - 2 * e.length)) return {
        changes: {
          insert: e + e + e + e,
          from: l9
        },
        effects: S5.of(l9 + e.length),
        range: x.cursor(l9 + e.length)
      };
      if (n11.charCategorizer(l9)(r2) != E.Word) {
        let c3 = n11.sliceDoc(l9 - 1, l9);
        if (c3 != e && n11.charCategorizer(l9)(c3) != E.Word && !Dt2(n11, l9, e)) return {
          changes: {
            insert: e + e,
            from: l9
          },
          effects: S5.of(l9 + e.length),
          range: x.cursor(l9 + e.length)
        };
      }
    }
    return {
      range: i2 = s45
    };
  });
  return i2 ? null : n11.update(o3, {
    scrollIntoView: true,
    userEvent: "input.type"
  });
}
function xe4(n11, e) {
  let t3 = m3(n11).resolveInner(e + 1);
  return t3.parent && t3.from == e;
}
function Dt2(n11, e, t3) {
  let i2 = m3(n11).resolveInner(e, -1);
  for (let o3 = 0; o3 < 5; o3++) {
    if (n11.sliceDoc(i2.from, i2.from + t3.length) == t3) return true;
    let s45 = i2.to == e && i2.parent;
    if (!s45) break;
    i2 = s45;
  }
  return false;
}
function Xt2(n11 = {}) {
  return [
    p,
    C5.of(n11),
    dt2,
    Ut3,
    Le4
  ];
}
var jt3 = [
  {
    key: "Ctrl-Space",
    run: ft3
  },
  {
    key: "Escape",
    run: ut
  },
  {
    key: "ArrowDown",
    run: L4(true)
  },
  {
    key: "ArrowUp",
    run: L4(false)
  },
  {
    key: "PageDown",
    run: L4(true, "page")
  },
  {
    key: "PageUp",
    run: L4(false, "page")
  },
  {
    key: "Enter",
    run: at4
  }
];
var Ut3 = lt.highest(ur.computeN([
  C5
], (n11) => n11.facet(C5).defaultKeymap ? [
  jt3
] : []));
export {
  I as EditorState,
  M2 as EditorView,
  pt2 as StreamLanguage,
  Xt2 as autocompletion,
  Ge3 as completeFromList,
  rn2 as defaultHighlightStyle,
  go as lineNumbers,
  en2 as syntaxHighlighting
};
