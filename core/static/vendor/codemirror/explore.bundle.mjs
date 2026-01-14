// deno:https://esm.sh/@codemirror/state@0.20.1/denonext/state.mjs
var m = class s {
  constructor() {
  }
  lineAt(e4) {
    if (e4 < 0 || e4 > this.length) throw new RangeError(`Invalid position ${e4} in document of length ${this.length}`);
    return this.lineInner(e4, false, 1, 0);
  }
  line(e4) {
    if (e4 < 1 || e4 > this.lines) throw new RangeError(`Invalid line number ${e4} in ${this.lines}-line document`);
    return this.lineInner(e4, true, 1, 0);
  }
  replace(e4, t5, n22) {
    let i9 = [];
    return this.decompose(0, e4, i9, 2), n22.length && n22.decompose(0, n22.length, i9, 3), this.decompose(t5, this.length, i9, 1), N.from(i9, this.length - (t5 - e4) + n22.length);
  }
  append(e4) {
    return this.replace(this.length, this.length, e4);
  }
  slice(e4, t5 = this.length) {
    let n22 = [];
    return this.decompose(e4, t5, n22, 0), N.from(n22, t5 - e4);
  }
  eq(e4) {
    if (e4 == this) return true;
    if (e4.length != this.length || e4.lines != this.lines) return false;
    let t5 = this.scanIdentical(e4, 1), n22 = this.length - this.scanIdentical(e4, -1), i9 = new B(this), r2 = new B(e4);
    for (let l11 = t5, h3 = t5; ; ) {
      if (i9.next(l11), r2.next(l11), l11 = 0, i9.lineBreak != r2.lineBreak || i9.done != r2.done || i9.value != r2.value) return false;
      if (h3 += i9.value.length, i9.done || h3 >= n22) return true;
    }
  }
  iter(e4 = 1) {
    return new B(this, e4);
  }
  iterRange(e4, t5 = this.length) {
    return new X(this, e4, t5);
  }
  iterLines(e4, t5) {
    let n22;
    if (e4 == null) n22 = this.iter();
    else {
      t5 == null && (t5 = this.lines + 1);
      let i9 = this.line(e4).from;
      n22 = this.iterRange(i9, Math.max(i9, t5 == this.lines + 1 ? this.length : t5 <= 1 ? 0 : this.line(t5 - 1).to));
    }
    return new Y(n22);
  }
  toString() {
    return this.sliceString(0);
  }
  toJSON() {
    let e4 = [];
    return this.flatten(e4), e4;
  }
  static of(e4) {
    if (e4.length == 0) throw new RangeError("A document must have at least one line");
    return e4.length == 1 && !e4[0] ? s.empty : e4.length <= 32 ? new k(e4) : N.from(k.split(e4, []));
  }
};
var k = class s2 extends m {
  constructor(e4, t5 = je(e4)) {
    super(), this.text = e4, this.length = t5;
  }
  get lines() {
    return this.text.length;
  }
  get children() {
    return null;
  }
  lineInner(e4, t5, n22, i9) {
    for (let r2 = 0; ; r2++) {
      let l11 = this.text[r2], h3 = i9 + l11.length;
      if ((t5 ? n22 : h3) >= e4) return new ae(i9, h3, n22, l11);
      i9 = h3 + 1, n22++;
    }
  }
  decompose(e4, t5, n22, i9) {
    let r2 = e4 <= 0 && t5 >= this.length ? this : new s2(Ie(this.text, e4, t5), Math.min(t5, this.length) - Math.max(0, e4));
    if (i9 & 1) {
      let l11 = n22.pop(), h3 = Q(r2.text, l11.text.slice(), 0, r2.length);
      if (h3.length <= 32) n22.push(new s2(h3, l11.length + r2.length));
      else {
        let o4 = h3.length >> 1;
        n22.push(new s2(h3.slice(0, o4)), new s2(h3.slice(o4)));
      }
    } else n22.push(r2);
  }
  replace(e4, t5, n22) {
    if (!(n22 instanceof s2)) return super.replace(e4, t5, n22);
    let i9 = Q(this.text, Q(n22.text, Ie(this.text, 0, e4)), t5), r2 = this.length + n22.length - (t5 - e4);
    return i9.length <= 32 ? new s2(i9, r2) : N.from(s2.split(i9, []), r2);
  }
  sliceString(e4, t5 = this.length, n22 = `
`) {
    let i9 = "";
    for (let r2 = 0, l11 = 0; r2 <= t5 && l11 < this.text.length; l11++) {
      let h3 = this.text[l11], o4 = r2 + h3.length;
      r2 > e4 && l11 && (i9 += n22), e4 < o4 && t5 > r2 && (i9 += h3.slice(Math.max(0, e4 - r2), t5 - r2)), r2 = o4 + 1;
    }
    return i9;
  }
  flatten(e4) {
    for (let t5 of this.text) e4.push(t5);
  }
  scanIdentical() {
    return 0;
  }
  static split(e4, t5) {
    let n22 = [], i9 = -1;
    for (let r2 of e4) n22.push(r2), i9 += r2.length + 1, n22.length == 32 && (t5.push(new s2(n22, i9)), n22 = [], i9 = -1);
    return i9 > -1 && t5.push(new s2(n22, i9)), t5;
  }
};
var N = class s3 extends m {
  constructor(e4, t5) {
    super(), this.children = e4, this.length = t5, this.lines = 0;
    for (let n22 of e4) this.lines += n22.lines;
  }
  lineInner(e4, t5, n22, i9) {
    for (let r2 = 0; ; r2++) {
      let l11 = this.children[r2], h3 = i9 + l11.length, o4 = n22 + l11.lines - 1;
      if ((t5 ? o4 : h3) >= e4) return l11.lineInner(e4, t5, n22, i9);
      i9 = h3 + 1, n22 = o4 + 1;
    }
  }
  decompose(e4, t5, n22, i9) {
    for (let r2 = 0, l11 = 0; l11 <= t5 && r2 < this.children.length; r2++) {
      let h3 = this.children[r2], o4 = l11 + h3.length;
      if (e4 <= o4 && t5 >= l11) {
        let a2 = i9 & ((l11 <= e4 ? 1 : 0) | (o4 >= t5 ? 2 : 0));
        l11 >= e4 && o4 <= t5 && !a2 ? n22.push(h3) : h3.decompose(e4 - l11, t5 - l11, n22, a2);
      }
      l11 = o4 + 1;
    }
  }
  replace(e4, t5, n22) {
    if (n22.lines < this.lines) for (let i9 = 0, r2 = 0; i9 < this.children.length; i9++) {
      let l11 = this.children[i9], h3 = r2 + l11.length;
      if (e4 >= r2 && t5 <= h3) {
        let o4 = l11.replace(e4 - r2, t5 - r2, n22), a2 = this.lines - l11.lines + o4.lines;
        if (o4.lines < a2 >> 4 && o4.lines > a2 >> 6) {
          let f2 = this.children.slice();
          return f2[i9] = o4, new s3(f2, this.length - (t5 - e4) + n22.length);
        }
        return super.replace(r2, h3, o4);
      }
      r2 = h3 + 1;
    }
    return super.replace(e4, t5, n22);
  }
  sliceString(e4, t5 = this.length, n22 = `
`) {
    let i9 = "";
    for (let r2 = 0, l11 = 0; r2 < this.children.length && l11 <= t5; r2++) {
      let h3 = this.children[r2], o4 = l11 + h3.length;
      l11 > e4 && r2 && (i9 += n22), e4 < o4 && t5 > l11 && (i9 += h3.sliceString(e4 - l11, t5 - l11, n22)), l11 = o4 + 1;
    }
    return i9;
  }
  flatten(e4) {
    for (let t5 of this.children) t5.flatten(e4);
  }
  scanIdentical(e4, t5) {
    if (!(e4 instanceof s3)) return 0;
    let n22 = 0, [i9, r2, l11, h3] = t5 > 0 ? [
      0,
      0,
      this.children.length,
      e4.children.length
    ] : [
      this.children.length - 1,
      e4.children.length - 1,
      -1,
      -1
    ];
    for (; ; i9 += t5, r2 += t5) {
      if (i9 == l11 || r2 == h3) return n22;
      let o4 = this.children[i9], a2 = e4.children[r2];
      if (o4 != a2) return n22 + o4.scanIdentical(a2, t5);
      n22 += o4.length + 1;
    }
  }
  static from(e4, t5 = e4.reduce((n22, i9) => n22 + i9.length + 1, -1)) {
    let n22 = 0;
    for (let d5 of e4) n22 += d5.lines;
    if (n22 < 32) {
      let d5 = [];
      for (let g6 of e4) g6.flatten(d5);
      return new k(d5, t5);
    }
    let i9 = Math.max(32, n22 >> 5), r2 = i9 << 1, l11 = i9 >> 1, h3 = [], o4 = 0, a2 = -1, f2 = [];
    function u5(d5) {
      let g6;
      if (d5.lines > r2 && d5 instanceof s3) for (let A11 of d5.children) u5(A11);
      else d5.lines > l11 && (o4 > l11 || !o4) ? (c4(), h3.push(d5)) : d5 instanceof k && o4 && (g6 = f2[f2.length - 1]) instanceof k && d5.lines + g6.lines <= 32 ? (o4 += d5.lines, a2 += d5.length + 1, f2[f2.length - 1] = new k(g6.text.concat(d5.text), g6.length + 1 + d5.length)) : (o4 + d5.lines > i9 && c4(), o4 += d5.lines, a2 += d5.length + 1, f2.push(d5));
    }
    function c4() {
      o4 != 0 && (h3.push(f2.length == 1 ? f2[0] : s3.from(f2, a2)), a2 = -1, o4 = f2.length = 0);
    }
    for (let d5 of e4) u5(d5);
    return c4(), h3.length == 1 ? h3[0] : new s3(h3, t5);
  }
};
m.empty = new k([
  ""
], 0);
function je(s99) {
  let e4 = -1;
  for (let t5 of s99) e4 += t5.length + 1;
  return e4;
}
function Q(s99, e4, t5 = 0, n22 = 1e9) {
  for (let i9 = 0, r2 = 0, l11 = true; r2 < s99.length && i9 <= n22; r2++) {
    let h3 = s99[r2], o4 = i9 + h3.length;
    o4 >= t5 && (o4 > n22 && (h3 = h3.slice(0, n22 - i9)), i9 < t5 && (h3 = h3.slice(t5 - i9)), l11 ? (e4[e4.length - 1] += h3, l11 = false) : e4.push(h3)), i9 = o4 + 1;
  }
  return e4;
}
function Ie(s99, e4, t5) {
  return Q(s99, [
    ""
  ], e4, t5);
}
var B = class {
  constructor(e4, t5 = 1) {
    this.dir = t5, this.done = false, this.lineBreak = false, this.value = "", this.nodes = [
      e4
    ], this.offsets = [
      t5 > 0 ? 1 : (e4 instanceof k ? e4.text.length : e4.children.length) << 1
    ];
  }
  nextInner(e4, t5) {
    for (this.done = this.lineBreak = false; ; ) {
      let n22 = this.nodes.length - 1, i9 = this.nodes[n22], r2 = this.offsets[n22], l11 = r2 >> 1, h3 = i9 instanceof k ? i9.text.length : i9.children.length;
      if (l11 == (t5 > 0 ? h3 : 0)) {
        if (n22 == 0) return this.done = true, this.value = "", this;
        t5 > 0 && this.offsets[n22 - 1]++, this.nodes.pop(), this.offsets.pop();
      } else if ((r2 & 1) == (t5 > 0 ? 0 : 1)) {
        if (this.offsets[n22] += t5, e4 == 0) return this.lineBreak = true, this.value = `
`, this;
        e4--;
      } else if (i9 instanceof k) {
        let o4 = i9.text[l11 + (t5 < 0 ? -1 : 0)];
        if (this.offsets[n22] += t5, o4.length > Math.max(0, e4)) return this.value = e4 == 0 ? o4 : t5 > 0 ? o4.slice(e4) : o4.slice(0, o4.length - e4), this;
        e4 -= o4.length;
      } else {
        let o4 = i9.children[l11 + (t5 < 0 ? -1 : 0)];
        e4 > o4.length ? (e4 -= o4.length, this.offsets[n22] += t5) : (t5 < 0 && this.offsets[n22]--, this.nodes.push(o4), this.offsets.push(t5 > 0 ? 1 : (o4 instanceof k ? o4.text.length : o4.children.length) << 1));
      }
    }
  }
  next(e4 = 0) {
    return e4 < 0 && (this.nextInner(-e4, -this.dir), e4 = this.value.length), this.nextInner(e4, this.dir);
  }
};
var X = class {
  constructor(e4, t5, n22) {
    this.value = "", this.done = false, this.cursor = new B(e4, t5 > n22 ? -1 : 1), this.pos = t5 > n22 ? e4.length : 0, this.from = Math.min(t5, n22), this.to = Math.max(t5, n22);
  }
  nextInner(e4, t5) {
    if (t5 < 0 ? this.pos <= this.from : this.pos >= this.to) return this.value = "", this.done = true, this;
    e4 += Math.max(0, t5 < 0 ? this.pos - this.to : this.from - this.pos);
    let n22 = t5 < 0 ? this.pos - this.from : this.to - this.pos;
    e4 > n22 && (e4 = n22), n22 -= e4;
    let { value: i9 } = this.cursor.next(e4);
    return this.pos += (i9.length + e4) * t5, this.value = i9.length <= n22 ? i9 : t5 < 0 ? i9.slice(i9.length - n22) : i9.slice(0, n22), this.done = !this.value, this;
  }
  next(e4 = 0) {
    return e4 < 0 ? e4 = Math.max(e4, this.from - this.pos) : e4 > 0 && (e4 = Math.min(e4, this.to - this.pos)), this.nextInner(e4, this.cursor.dir);
  }
  get lineBreak() {
    return this.cursor.lineBreak && this.value != "";
  }
};
var Y = class {
  constructor(e4) {
    this.inner = e4, this.afterBreak = true, this.value = "", this.done = false;
  }
  next(e4 = 0) {
    let { done: t5, lineBreak: n22, value: i9 } = this.inner.next(e4);
    return t5 ? (this.done = true, this.value = "") : n22 ? this.afterBreak ? this.value = "" : (this.afterBreak = true, this.next()) : (this.value = i9, this.afterBreak = false), this;
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
  constructor(e4, t5, n22, i9) {
    this.from = e4, this.to = t5, this.number = n22, this.text = i9;
  }
  get length() {
    return this.to - this.from;
  }
};
var D = "lc,34,7n,7,7b,19,,,,2,,2,,,20,b,1c,l,g,,2t,7,2,6,2,2,,4,z,,u,r,2j,b,1m,9,9,,o,4,,9,,3,,5,17,3,3b,f,,w,1j,,,,4,8,4,,3,7,a,2,t,,1m,,,,2,4,8,,9,,a,2,q,,2,2,1l,,4,2,4,2,2,3,3,,u,2,3,,b,2,1l,,4,5,,2,4,,k,2,m,6,,,1m,,,2,,4,8,,7,3,a,2,u,,1n,,,,c,,9,,14,,3,,1l,3,5,3,,4,7,2,b,2,t,,1m,,2,,2,,3,,5,2,7,2,b,2,s,2,1l,2,,,2,4,8,,9,,a,2,t,,20,,4,,2,3,,,8,,29,,2,7,c,8,2q,,2,9,b,6,22,2,r,,,,,,1j,e,,5,,2,5,b,,10,9,,2u,4,,6,,2,2,2,p,2,4,3,g,4,d,,2,2,6,,f,,jj,3,qa,3,t,3,t,2,u,2,1s,2,,7,8,,2,b,9,,19,3,3b,2,y,,3a,3,4,2,9,,6,3,63,2,2,,1m,,,7,,,,,2,8,6,a,2,,1c,h,1r,4,1c,7,,,5,,14,9,c,2,w,4,2,2,,3,1k,,,2,3,,,3,1m,8,2,2,48,3,,d,,7,4,,6,,3,2,5i,1m,,5,ek,,5f,x,2da,3,3x,,2o,w,fe,6,2x,2,n9w,4,,a,w,2,28,2,7k,,3,,4,,p,2,5,,47,2,q,i,d,,12,8,p,b,1a,3,1c,,2,4,2,2,13,,1v,6,2,2,2,2,c,,8,,1b,,1f,,,3,2,2,5,2,,,16,2,8,,6m,,2,,4,,fn4,,kh,g,g,g,a6,2,gt,,6a,,45,5,1ae,3,,2,5,4,14,3,4,,4l,2,fx,4,ar,2,49,b,4w,,1i,f,1k,3,1d,4,2,2,1x,3,10,5,,8,1q,,c,2,1g,9,a,4,2,,2n,3,2,,,2,6,,4g,,3,8,l,2,1l,2,,,,,m,,e,7,3,5,5f,8,2,3,,,n,,29,,2,6,,,2,,,2,,2,6j,,2,4,6,2,,2,r,2,2d,8,2,,,2,2y,,,,2,6,,,2t,3,2,4,,5,77,9,,2,6t,,a,2,,,4,,40,4,2,2,4,,w,a,14,6,2,4,8,,9,6,2,3,1a,d,,2,ba,7,,6,,,2a,m,2,7,,2,,2,3e,6,3,,,2,,7,,,20,2,3,,,,9n,2,f0b,5,1n,7,t4,,1r,4,29,,f5k,2,43q,,,3,4,5,8,8,2,7,u,4,44,3,1iz,1j,4,1e,8,,e,,m,5,,f,11s,7,,h,2,7,,2,,5,79,7,c5,4,15s,7,31,7,240,5,gx7k,2o,3k,6o".split(",").map((s99) => s99 ? parseInt(s99, 36) : 1);
for (let s99 = 1; s99 < D.length; s99++) D[s99] += D[s99 - 1];
function He(s99) {
  for (let e4 = 1; e4 < D.length; e4 += 2) if (D[e4] > s99) return D[e4 - 1] <= s99;
  return false;
}
function Ae(s99) {
  return s99 >= 127462 && s99 <= 127487;
}
var Pe = 8205;
function _(s99, e4, t5 = true, n22 = true) {
  return (t5 ? Ce : Ze)(s99, e4, n22);
}
function Ce(s99, e4, t5) {
  if (e4 == s99.length) return e4;
  e4 && Me(s99.charCodeAt(e4)) && Fe(s99.charCodeAt(e4 - 1)) && e4--;
  let n22 = he(s99, e4);
  for (e4 += be(n22); e4 < s99.length; ) {
    let i9 = he(s99, e4);
    if (n22 == Pe || i9 == Pe || t5 && He(i9)) e4 += be(i9), n22 = i9;
    else if (Ae(i9)) {
      let r2 = 0, l11 = e4 - 2;
      for (; l11 >= 0 && Ae(he(s99, l11)); ) r2++, l11 -= 2;
      if (r2 % 2 == 0) break;
      e4 += 2;
    } else break;
  }
  return e4;
}
function Ze(s99, e4, t5) {
  for (; e4 > 0; ) {
    let n22 = Ce(s99, e4 - 2, t5);
    if (n22 < e4) return n22;
    e4--;
  }
  return 0;
}
function Me(s99) {
  return s99 >= 56320 && s99 < 57344;
}
function Fe(s99) {
  return s99 >= 55296 && s99 < 56320;
}
function he(s99, e4) {
  let t5 = s99.charCodeAt(e4);
  if (!Fe(t5) || e4 + 1 == s99.length) return t5;
  let n22 = s99.charCodeAt(e4 + 1);
  return Me(n22) ? (t5 - 55296 << 10) + (n22 - 56320) + 65536 : t5;
}
function rt(s99) {
  return s99 <= 65535 ? String.fromCharCode(s99) : (s99 -= 65536, String.fromCharCode((s99 >> 10) + 55296, (s99 & 1023) + 56320));
}
function be(s99) {
  return s99 < 65536 ? 1 : 2;
}
var fe = /\r\n?|\n/;
var b = function(s99) {
  return s99[s99.Simple = 0] = "Simple", s99[s99.TrackDel = 1] = "TrackDel", s99[s99.TrackBefore = 2] = "TrackBefore", s99[s99.TrackAfter = 3] = "TrackAfter", s99;
}(b || (b = {}));
var C = class s4 {
  constructor(e4) {
    this.sections = e4;
  }
  get length() {
    let e4 = 0;
    for (let t5 = 0; t5 < this.sections.length; t5 += 2) e4 += this.sections[t5];
    return e4;
  }
  get newLength() {
    let e4 = 0;
    for (let t5 = 0; t5 < this.sections.length; t5 += 2) {
      let n22 = this.sections[t5 + 1];
      e4 += n22 < 0 ? this.sections[t5] : n22;
    }
    return e4;
  }
  get empty() {
    return this.sections.length == 0 || this.sections.length == 2 && this.sections[1] < 0;
  }
  iterGaps(e4) {
    for (let t5 = 0, n22 = 0, i9 = 0; t5 < this.sections.length; ) {
      let r2 = this.sections[t5++], l11 = this.sections[t5++];
      l11 < 0 ? (e4(n22, i9, r2), i9 += r2) : i9 += l11, n22 += r2;
    }
  }
  iterChangedRanges(e4, t5 = false) {
    ue(this, e4, t5);
  }
  get invertedDesc() {
    let e4 = [];
    for (let t5 = 0; t5 < this.sections.length; ) {
      let n22 = this.sections[t5++], i9 = this.sections[t5++];
      i9 < 0 ? e4.push(n22, i9) : e4.push(i9, n22);
    }
    return new s4(e4);
  }
  composeDesc(e4) {
    return this.empty ? e4 : e4.empty ? this : Je(this, e4);
  }
  mapDesc(e4, t5 = false) {
    return e4.empty ? this : ce(this, e4, t5);
  }
  mapPos(e4, t5 = -1, n22 = b.Simple) {
    let i9 = 0, r2 = 0;
    for (let l11 = 0; l11 < this.sections.length; ) {
      let h3 = this.sections[l11++], o4 = this.sections[l11++], a2 = i9 + h3;
      if (o4 < 0) {
        if (a2 > e4) return r2 + (e4 - i9);
        r2 += h3;
      } else {
        if (n22 != b.Simple && a2 >= e4 && (n22 == b.TrackDel && i9 < e4 && a2 > e4 || n22 == b.TrackBefore && i9 < e4 || n22 == b.TrackAfter && a2 > e4)) return null;
        if (a2 > e4 || a2 == e4 && t5 < 0 && !h3) return e4 == i9 || t5 < 0 ? r2 : r2 + o4;
        r2 += o4;
      }
      i9 = a2;
    }
    if (e4 > i9) throw new RangeError(`Position ${e4} is out of range for changeset of length ${i9}`);
    return r2;
  }
  touchesRange(e4, t5 = e4) {
    for (let n22 = 0, i9 = 0; n22 < this.sections.length && i9 <= t5; ) {
      let r2 = this.sections[n22++], l11 = this.sections[n22++], h3 = i9 + r2;
      if (l11 >= 0 && i9 <= t5 && h3 >= e4) return i9 < e4 && h3 > t5 ? "cover" : true;
      i9 = h3;
    }
    return false;
  }
  toString() {
    let e4 = "";
    for (let t5 = 0; t5 < this.sections.length; ) {
      let n22 = this.sections[t5++], i9 = this.sections[t5++];
      e4 += (e4 ? " " : "") + n22 + (i9 >= 0 ? ":" + i9 : "");
    }
    return e4;
  }
  toJSON() {
    return this.sections;
  }
  static fromJSON(e4) {
    if (!Array.isArray(e4) || e4.length % 2 || e4.some((t5) => typeof t5 != "number")) throw new RangeError("Invalid JSON representation of ChangeDesc");
    return new s4(e4);
  }
  static create(e4) {
    return new s4(e4);
  }
};
var P = class s5 extends C {
  constructor(e4, t5) {
    super(e4), this.inserted = t5;
  }
  apply(e4) {
    if (this.length != e4.length) throw new RangeError("Applying change set to a document with the wrong length");
    return ue(this, (t5, n22, i9, r2, l11) => e4 = e4.replace(i9, i9 + (n22 - t5), l11), false), e4;
  }
  mapDesc(e4, t5 = false) {
    return ce(this, e4, t5, true);
  }
  invert(e4) {
    let t5 = this.sections.slice(), n22 = [];
    for (let i9 = 0, r2 = 0; i9 < t5.length; i9 += 2) {
      let l11 = t5[i9], h3 = t5[i9 + 1];
      if (h3 >= 0) {
        t5[i9] = h3, t5[i9 + 1] = l11;
        let o4 = i9 >> 1;
        for (; n22.length < o4; ) n22.push(m.empty);
        n22.push(l11 ? e4.slice(r2, r2 + l11) : m.empty);
      }
      r2 += l11;
    }
    return new s5(t5, n22);
  }
  compose(e4) {
    return this.empty ? e4 : e4.empty ? this : Je(this, e4, true);
  }
  map(e4, t5 = false) {
    return e4.empty ? this : ce(this, e4, t5, true);
  }
  iterChanges(e4, t5 = false) {
    ue(this, e4, t5);
  }
  get desc() {
    return C.create(this.sections);
  }
  filter(e4) {
    let t5 = [], n22 = [], i9 = [], r2 = new M(this);
    e: for (let l11 = 0, h3 = 0; ; ) {
      let o4 = l11 == e4.length ? 1e9 : e4[l11++];
      for (; h3 < o4 || h3 == o4 && r2.len == 0; ) {
        if (r2.done) break e;
        let f2 = Math.min(r2.len, o4 - h3);
        w(i9, f2, -1);
        let u5 = r2.ins == -1 ? -1 : r2.off == 0 ? r2.ins : 0;
        w(t5, f2, u5), u5 > 0 && R(n22, t5, r2.text), r2.forward(f2), h3 += f2;
      }
      let a2 = e4[l11++];
      for (; h3 < a2; ) {
        if (r2.done) break e;
        let f2 = Math.min(r2.len, a2 - h3);
        w(t5, f2, -1), w(i9, f2, r2.ins == -1 ? -1 : r2.off == 0 ? r2.ins : 0), r2.forward(f2), h3 += f2;
      }
    }
    return {
      changes: new s5(t5, n22),
      filtered: C.create(i9)
    };
  }
  toJSON() {
    let e4 = [];
    for (let t5 = 0; t5 < this.sections.length; t5 += 2) {
      let n22 = this.sections[t5], i9 = this.sections[t5 + 1];
      i9 < 0 ? e4.push(n22) : i9 == 0 ? e4.push([
        n22
      ]) : e4.push([
        n22
      ].concat(this.inserted[t5 >> 1].toJSON()));
    }
    return e4;
  }
  static of(e4, t5, n22) {
    let i9 = [], r2 = [], l11 = 0, h3 = null;
    function o4(f2 = false) {
      if (!f2 && !i9.length) return;
      l11 < t5 && w(i9, t5 - l11, -1);
      let u5 = new s5(i9, r2);
      h3 = h3 ? h3.compose(u5.map(h3)) : u5, i9 = [], r2 = [], l11 = 0;
    }
    function a2(f2) {
      if (Array.isArray(f2)) for (let u5 of f2) a2(u5);
      else if (f2 instanceof s5) {
        if (f2.length != t5) throw new RangeError(`Mismatched change set length (got ${f2.length}, expected ${t5})`);
        o4(), h3 = h3 ? h3.compose(f2.map(h3)) : f2;
      } else {
        let { from: u5, to: c4 = u5, insert: d5 } = f2;
        if (u5 > c4 || u5 < 0 || c4 > t5) throw new RangeError(`Invalid change range ${u5} to ${c4} (in doc of length ${t5})`);
        let g6 = d5 ? typeof d5 == "string" ? m.of(d5.split(n22 || fe)) : d5 : m.empty, A11 = g6.length;
        if (u5 == c4 && A11 == 0) return;
        u5 < l11 && o4(), u5 > l11 && w(i9, u5 - l11, -1), w(i9, c4 - u5, A11), R(r2, i9, g6), l11 = c4;
      }
    }
    return a2(e4), o4(!h3), h3;
  }
  static empty(e4) {
    return new s5(e4 ? [
      e4,
      -1
    ] : [], []);
  }
  static fromJSON(e4) {
    if (!Array.isArray(e4)) throw new RangeError("Invalid JSON representation of ChangeSet");
    let t5 = [], n22 = [];
    for (let i9 = 0; i9 < e4.length; i9++) {
      let r2 = e4[i9];
      if (typeof r2 == "number") t5.push(r2, -1);
      else {
        if (!Array.isArray(r2) || typeof r2[0] != "number" || r2.some((l11, h3) => h3 && typeof l11 != "string")) throw new RangeError("Invalid JSON representation of ChangeSet");
        if (r2.length == 1) t5.push(r2[0], 0);
        else {
          for (; n22.length < i9; ) n22.push(m.empty);
          n22[i9] = m.of(r2.slice(1)), t5.push(r2[0], n22[i9].length);
        }
      }
    }
    return new s5(t5, n22);
  }
  static createSet(e4, t5) {
    return new s5(e4, t5);
  }
};
function w(s99, e4, t5, n22 = false) {
  if (e4 == 0 && t5 <= 0) return;
  let i9 = s99.length - 2;
  i9 >= 0 && t5 <= 0 && t5 == s99[i9 + 1] ? s99[i9] += e4 : e4 == 0 && s99[i9] == 0 ? s99[i9 + 1] += t5 : n22 ? (s99[i9] += e4, s99[i9 + 1] += t5) : s99.push(e4, t5);
}
function R(s99, e4, t5) {
  if (t5.length == 0) return;
  let n22 = e4.length - 2 >> 1;
  if (n22 < s99.length) s99[s99.length - 1] = s99[s99.length - 1].append(t5);
  else {
    for (; s99.length < n22; ) s99.push(m.empty);
    s99.push(t5);
  }
}
function ue(s99, e4, t5) {
  let n22 = s99.inserted;
  for (let i9 = 0, r2 = 0, l11 = 0; l11 < s99.sections.length; ) {
    let h3 = s99.sections[l11++], o4 = s99.sections[l11++];
    if (o4 < 0) i9 += h3, r2 += h3;
    else {
      let a2 = i9, f2 = r2, u5 = m.empty;
      for (; a2 += h3, f2 += o4, o4 && n22 && (u5 = u5.append(n22[l11 - 2 >> 1])), !(t5 || l11 == s99.sections.length || s99.sections[l11 + 1] < 0); ) h3 = s99.sections[l11++], o4 = s99.sections[l11++];
      e4(i9, a2, r2, f2, u5), i9 = a2, r2 = f2;
    }
  }
}
function ce(s99, e4, t5, n22 = false) {
  let i9 = [], r2 = n22 ? [] : null, l11 = new M(s99), h3 = new M(e4);
  for (let o4 = 0, a2 = 0; ; ) if (l11.ins == -1) o4 += l11.len, l11.next();
  else if (h3.ins == -1 && a2 < o4) {
    let f2 = Math.min(h3.len, o4 - a2);
    h3.forward(f2), w(i9, f2, -1), a2 += f2;
  } else if (h3.ins >= 0 && (l11.done || a2 < o4 || a2 == o4 && (h3.len < l11.len || h3.len == l11.len && !t5))) {
    for (w(i9, h3.ins, -1); o4 > a2 && !l11.done && o4 + l11.len < a2 + h3.len; ) o4 += l11.len, l11.next();
    a2 += h3.len, h3.next();
  } else if (l11.ins >= 0) {
    let f2 = 0, u5 = o4 + l11.len;
    for (; ; ) if (h3.ins >= 0 && a2 > o4 && a2 + h3.len < u5) f2 += h3.ins, a2 += h3.len, h3.next();
    else if (h3.ins == -1 && a2 < u5) {
      let c4 = Math.min(h3.len, u5 - a2);
      f2 += c4, h3.forward(c4), a2 += c4;
    } else break;
    w(i9, f2, l11.ins), r2 && R(r2, i9, l11.text), o4 = u5, l11.next();
  } else {
    if (l11.done && h3.done) return r2 ? P.createSet(i9, r2) : C.create(i9);
    throw new Error("Mismatched change set lengths");
  }
}
function Je(s99, e4, t5 = false) {
  let n22 = [], i9 = t5 ? [] : null, r2 = new M(s99), l11 = new M(e4);
  for (let h3 = false; ; ) {
    if (r2.done && l11.done) return i9 ? P.createSet(n22, i9) : C.create(n22);
    if (r2.ins == 0) w(n22, r2.len, 0, h3), r2.next();
    else if (l11.len == 0 && !l11.done) w(n22, 0, l11.ins, h3), i9 && R(i9, n22, l11.text), l11.next();
    else {
      if (r2.done || l11.done) throw new Error("Mismatched change set lengths");
      {
        let o4 = Math.min(r2.len2, l11.len), a2 = n22.length;
        if (r2.ins == -1) {
          let f2 = l11.ins == -1 ? -1 : l11.off ? 0 : l11.ins;
          w(n22, o4, f2, h3), i9 && f2 && R(i9, n22, l11.text);
        } else l11.ins == -1 ? (w(n22, r2.off ? 0 : r2.len, o4, h3), i9 && R(i9, n22, r2.textBit(o4))) : (w(n22, r2.off ? 0 : r2.len, l11.off ? 0 : l11.ins, h3), i9 && !l11.off && R(i9, n22, l11.text));
        h3 = (r2.ins > o4 || l11.ins >= 0 && l11.len > o4) && (h3 || n22.length > a2), r2.forward2(o4), l11.forward(o4);
      }
    }
  }
}
var M = class {
  constructor(e4) {
    this.set = e4, this.i = 0, this.next();
  }
  next() {
    let { sections: e4 } = this.set;
    this.i < e4.length ? (this.len = e4[this.i++], this.ins = e4[this.i++]) : (this.len = 0, this.ins = -2), this.off = 0;
  }
  get done() {
    return this.ins == -2;
  }
  get len2() {
    return this.ins < 0 ? this.len : this.ins;
  }
  get text() {
    let { inserted: e4 } = this.set, t5 = this.i - 2 >> 1;
    return t5 >= e4.length ? m.empty : e4[t5];
  }
  textBit(e4) {
    let { inserted: t5 } = this.set, n22 = this.i - 2 >> 1;
    return n22 >= t5.length && !e4 ? m.empty : t5[n22].slice(this.off, e4 == null ? void 0 : this.off + e4);
  }
  forward(e4) {
    e4 == this.len ? this.next() : (this.len -= e4, this.off += e4);
  }
  forward2(e4) {
    this.ins == -1 ? this.forward(e4) : e4 == this.ins ? this.next() : (this.ins -= e4, this.off += e4);
  }
};
var L = class s6 {
  constructor(e4, t5, n22) {
    this.from = e4, this.to = t5, this.flags = n22;
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
    let e4 = this.flags & 3;
    return e4 == 3 ? null : e4;
  }
  get goalColumn() {
    let e4 = this.flags >> 5;
    return e4 == 33554431 ? void 0 : e4;
  }
  map(e4, t5 = -1) {
    let n22, i9;
    return this.empty ? n22 = i9 = e4.mapPos(this.from, t5) : (n22 = e4.mapPos(this.from, 1), i9 = e4.mapPos(this.to, -1)), n22 == this.from && i9 == this.to ? this : new s6(n22, i9, this.flags);
  }
  extend(e4, t5 = e4) {
    if (e4 <= this.anchor && t5 >= this.anchor) return x.range(e4, t5);
    let n22 = Math.abs(e4 - this.anchor) > Math.abs(t5 - this.anchor) ? e4 : t5;
    return x.range(this.anchor, n22);
  }
  eq(e4) {
    return this.anchor == e4.anchor && this.head == e4.head;
  }
  toJSON() {
    return {
      anchor: this.anchor,
      head: this.head
    };
  }
  static fromJSON(e4) {
    if (!e4 || typeof e4.anchor != "number" || typeof e4.head != "number") throw new RangeError("Invalid JSON representation for SelectionRange");
    return x.range(e4.anchor, e4.head);
  }
  static create(e4, t5, n22) {
    return new s6(e4, t5, n22);
  }
};
var x = class s7 {
  constructor(e4, t5) {
    this.ranges = e4, this.mainIndex = t5;
  }
  map(e4, t5 = -1) {
    return e4.empty ? this : s7.create(this.ranges.map((n22) => n22.map(e4, t5)), this.mainIndex);
  }
  eq(e4) {
    if (this.ranges.length != e4.ranges.length || this.mainIndex != e4.mainIndex) return false;
    for (let t5 = 0; t5 < this.ranges.length; t5++) if (!this.ranges[t5].eq(e4.ranges[t5])) return false;
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
  addRange(e4, t5 = true) {
    return s7.create([
      e4
    ].concat(this.ranges), t5 ? 0 : this.mainIndex + 1);
  }
  replaceRange(e4, t5 = this.mainIndex) {
    let n22 = this.ranges.slice();
    return n22[t5] = e4, s7.create(n22, this.mainIndex);
  }
  toJSON() {
    return {
      ranges: this.ranges.map((e4) => e4.toJSON()),
      main: this.mainIndex
    };
  }
  static fromJSON(e4) {
    if (!e4 || !Array.isArray(e4.ranges) || typeof e4.main != "number" || e4.main >= e4.ranges.length) throw new RangeError("Invalid JSON representation for EditorSelection");
    return new s7(e4.ranges.map((t5) => L.fromJSON(t5)), e4.main);
  }
  static single(e4, t5 = e4) {
    return new s7([
      s7.range(e4, t5)
    ], 0);
  }
  static create(e4, t5 = 0) {
    if (e4.length == 0) throw new RangeError("A selection needs at least one range");
    for (let n22 = 0, i9 = 0; i9 < e4.length; i9++) {
      let r2 = e4[i9];
      if (r2.empty ? r2.from <= n22 : r2.from < n22) return s7.normalized(e4.slice(), t5);
      n22 = r2.to;
    }
    return new s7(e4, t5);
  }
  static cursor(e4, t5 = 0, n22, i9) {
    return L.create(e4, e4, (t5 == 0 ? 0 : t5 < 0 ? 4 : 8) | (n22 == null ? 3 : Math.min(2, n22)) | (i9 ?? 33554431) << 5);
  }
  static range(e4, t5, n22) {
    let i9 = (n22 ?? 33554431) << 5;
    return t5 < e4 ? L.create(t5, e4, 16 | i9 | 8) : L.create(e4, t5, i9 | (t5 > e4 ? 4 : 0));
  }
  static normalized(e4, t5 = 0) {
    let n22 = e4[t5];
    e4.sort((i9, r2) => i9.from - r2.from), t5 = e4.indexOf(n22);
    for (let i9 = 1; i9 < e4.length; i9++) {
      let r2 = e4[i9], l11 = e4[i9 - 1];
      if (r2.empty ? r2.from <= l11.to : r2.from < l11.to) {
        let h3 = l11.from, o4 = Math.max(r2.to, l11.to);
        i9 <= t5 && t5--, e4.splice(--i9, 2, r2.anchor > r2.head ? s7.range(o4, h3) : s7.range(h3, o4));
      }
    }
    return new s7(e4, t5);
  }
};
function Le(s99, e4) {
  for (let t5 of s99.ranges) if (t5.to > e4) throw new RangeError("Selection points outside of document");
}
var ye = 0;
var y = class s8 {
  constructor(e4, t5, n22, i9, r2) {
    this.combine = e4, this.compareInput = t5, this.compare = n22, this.isStatic = i9, this.extensions = r2, this.id = ye++, this.default = e4([]);
  }
  static define(e4 = {}) {
    return new s8(e4.combine || ((t5) => t5), e4.compareInput || ((t5, n22) => t5 === n22), e4.compare || (e4.combine ? (t5, n22) => t5 === n22 : Se), !!e4.static, e4.enables);
  }
  of(e4) {
    return new V([], this, 0, e4);
  }
  compute(e4, t5) {
    if (this.isStatic) throw new Error("Can't compute a static facet");
    return new V(e4, this, 1, t5);
  }
  computeN(e4, t5) {
    if (this.isStatic) throw new Error("Can't compute a static facet");
    return new V(e4, this, 2, t5);
  }
  from(e4, t5) {
    return t5 || (t5 = (n22) => n22), this.compute([
      e4
    ], (n22) => t5(n22.field(e4)));
  }
};
function Se(s99, e4) {
  return s99 == e4 || s99.length == e4.length && s99.every((t5, n22) => t5 === e4[n22]);
}
var V = class {
  constructor(e4, t5, n22, i9) {
    this.dependencies = e4, this.facet = t5, this.type = n22, this.value = i9, this.id = ye++;
  }
  dynamicSlot(e4) {
    var t5;
    let n22 = this.value, i9 = this.facet.compareInput, r2 = this.id, l11 = e4[r2] >> 1, h3 = this.type == 2, o4 = false, a2 = false, f2 = [];
    for (let u5 of this.dependencies) u5 == "doc" ? o4 = true : u5 == "selection" ? a2 = true : (((t5 = e4[u5.id]) !== null && t5 !== void 0 ? t5 : 1) & 1) == 0 && f2.push(e4[u5.id]);
    return {
      create(u5) {
        return u5.values[l11] = n22(u5), 1;
      },
      update(u5, c4) {
        if (o4 && c4.docChanged || a2 && (c4.docChanged || c4.selection) || de(u5, f2)) {
          let d5 = n22(u5);
          if (h3 ? !Ee(d5, u5.values[l11], i9) : !i9(d5, u5.values[l11])) return u5.values[l11] = d5, 1;
        }
        return 0;
      },
      reconfigure: (u5, c4) => {
        let d5 = n22(u5), g6 = c4.config.address[r2];
        if (g6 != null) {
          let A11 = ie(c4, g6);
          if (this.dependencies.every((p5) => p5 instanceof y ? c4.facet(p5) === u5.facet(p5) : p5 instanceof $ ? c4.field(p5, false) == u5.field(p5, false) : true) || (h3 ? Ee(d5, A11, i9) : i9(d5, A11))) return u5.values[l11] = A11, 0;
        }
        return u5.values[l11] = d5, 1;
      }
    };
  }
};
function Ee(s99, e4, t5) {
  if (s99.length != e4.length) return false;
  for (let n22 = 0; n22 < s99.length; n22++) if (!t5(s99[n22], e4[n22])) return false;
  return true;
}
function de(s99, e4) {
  let t5 = false;
  for (let n22 of e4) U(s99, n22) & 1 && (t5 = true);
  return t5;
}
function Ke(s99, e4, t5) {
  let n22 = t5.map((o4) => s99[o4.id]), i9 = t5.map((o4) => o4.type), r2 = n22.filter((o4) => !(o4 & 1)), l11 = s99[e4.id] >> 1;
  function h3(o4) {
    let a2 = [];
    for (let f2 = 0; f2 < n22.length; f2++) {
      let u5 = ie(o4, n22[f2]);
      if (i9[f2] == 2) for (let c4 of u5) a2.push(c4);
      else a2.push(u5);
    }
    return e4.combine(a2);
  }
  return {
    create(o4) {
      for (let a2 of n22) U(o4, a2);
      return o4.values[l11] = h3(o4), 1;
    },
    update(o4, a2) {
      if (!de(o4, r2)) return 0;
      let f2 = h3(o4);
      return e4.compare(f2, o4.values[l11]) ? 0 : (o4.values[l11] = f2, 1);
    },
    reconfigure(o4, a2) {
      let f2 = de(o4, n22), u5 = a2.config.facets[e4.id], c4 = a2.facet(e4);
      if (u5 && !f2 && Se(t5, u5)) return o4.values[l11] = c4, 0;
      let d5 = h3(o4);
      return e4.compare(d5, c4) ? (o4.values[l11] = c4, 0) : (o4.values[l11] = d5, 1);
    }
  };
}
var Oe = y.define({
  static: true
});
var $ = class s9 {
  constructor(e4, t5, n22, i9, r2) {
    this.id = e4, this.createF = t5, this.updateF = n22, this.compareF = i9, this.spec = r2, this.provides = void 0;
  }
  static define(e4) {
    let t5 = new s9(ye++, e4.create, e4.update, e4.compare || ((n22, i9) => n22 === i9), e4);
    return e4.provide && (t5.provides = e4.provide(t5)), t5;
  }
  create(e4) {
    let t5 = e4.facet(Oe).find((n22) => n22.field == this);
    return (t5?.create || this.createF)(e4);
  }
  slot(e4) {
    let t5 = e4[this.id] >> 1;
    return {
      create: (n22) => (n22.values[t5] = this.create(n22), 1),
      update: (n22, i9) => {
        let r2 = n22.values[t5], l11 = this.updateF(r2, i9);
        return this.compareF(r2, l11) ? 0 : (n22.values[t5] = l11, 1);
      },
      reconfigure: (n22, i9) => i9.config.address[this.id] != null ? (n22.values[t5] = i9.field(this), 0) : (n22.values[t5] = this.create(n22), 1)
    };
  }
  init(e4) {
    return [
      this,
      Oe.of({
        field: this,
        create: e4
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
function W(s99) {
  return (e4) => new ee(e4, s99);
}
var lt = {
  highest: W(J.highest),
  high: W(J.high),
  default: W(J.default),
  low: W(J.low),
  lowest: W(J.lowest)
};
var ee = class {
  constructor(e4, t5) {
    this.inner = e4, this.prec = t5;
  }
};
var te = class s10 {
  of(e4) {
    return new G(this, e4);
  }
  reconfigure(e4) {
    return s10.reconfigure.of({
      compartment: this,
      extension: e4
    });
  }
  get(e4) {
    return e4.config.compartments.get(this);
  }
};
var G = class {
  constructor(e4, t5) {
    this.compartment = e4, this.inner = t5;
  }
};
var ne = class s11 {
  constructor(e4, t5, n22, i9, r2, l11) {
    for (this.base = e4, this.compartments = t5, this.dynamicSlots = n22, this.address = i9, this.staticValues = r2, this.facets = l11, this.statusTemplate = []; this.statusTemplate.length < n22.length; ) this.statusTemplate.push(0);
  }
  staticFacet(e4) {
    let t5 = this.address[e4.id];
    return t5 == null ? e4.default : this.staticValues[t5 >> 1];
  }
  static resolve(e4, t5, n22) {
    let i9 = [], r2 = /* @__PURE__ */ Object.create(null), l11 = /* @__PURE__ */ new Map();
    for (let c4 of Qe(e4, t5, l11)) c4 instanceof $ ? i9.push(c4) : (r2[c4.facet.id] || (r2[c4.facet.id] = [])).push(c4);
    let h3 = /* @__PURE__ */ Object.create(null), o4 = [], a2 = [];
    for (let c4 of i9) h3[c4.id] = a2.length << 1, a2.push((d5) => c4.slot(d5));
    let f2 = n22?.config.facets;
    for (let c4 in r2) {
      let d5 = r2[c4], g6 = d5[0].facet, A11 = f2 && f2[c4] || [];
      if (d5.every((p5) => p5.type == 0)) if (h3[g6.id] = o4.length << 1 | 1, Se(A11, d5)) o4.push(n22.facet(g6));
      else {
        let p5 = g6.combine(d5.map((le10) => le10.value));
        o4.push(n22 && g6.compare(p5, n22.facet(g6)) ? n22.facet(g6) : p5);
      }
      else {
        for (let p5 of d5) p5.type == 0 ? (h3[p5.id] = o4.length << 1 | 1, o4.push(p5.value)) : (h3[p5.id] = a2.length << 1, a2.push((le10) => p5.dynamicSlot(le10)));
        h3[g6.id] = a2.length << 1, a2.push((p5) => Ke(p5, g6, d5));
      }
    }
    let u5 = a2.map((c4) => c4(h3));
    return new s11(e4, l11, u5, h3, o4, r2);
  }
};
function Qe(s99, e4, t5) {
  let n22 = [
    [],
    [],
    [],
    [],
    []
  ], i9 = /* @__PURE__ */ new Map();
  function r2(l11, h3) {
    let o4 = i9.get(l11);
    if (o4 != null) {
      if (o4 <= h3) return;
      let a2 = n22[o4].indexOf(l11);
      a2 > -1 && n22[o4].splice(a2, 1), l11 instanceof G && t5.delete(l11.compartment);
    }
    if (i9.set(l11, h3), Array.isArray(l11)) for (let a2 of l11) r2(a2, h3);
    else if (l11 instanceof G) {
      if (t5.has(l11.compartment)) throw new RangeError("Duplicate use of compartment in extensions");
      let a2 = e4.get(l11.compartment) || l11.inner;
      t5.set(l11.compartment, a2), r2(a2, h3);
    } else if (l11 instanceof ee) r2(l11.inner, l11.prec);
    else if (l11 instanceof $) n22[h3].push(l11), l11.provides && r2(l11.provides, h3);
    else if (l11 instanceof V) n22[h3].push(l11), l11.facet.extensions && r2(l11.facet.extensions, h3);
    else {
      let a2 = l11.extension;
      if (!a2) throw new Error(`Unrecognized extension value in extension set (${l11}). This sometimes happens because multiple instances of @codemirror/state are loaded, breaking instanceof checks.`);
      r2(a2, h3);
    }
  }
  return r2(s99, J.default), n22.reduce((l11, h3) => l11.concat(h3));
}
function U(s99, e4) {
  if (e4 & 1) return 2;
  let t5 = e4 >> 1, n22 = s99.status[t5];
  if (n22 == 4) throw new Error("Cyclic dependency between fields and/or facets");
  if (n22 & 2) return n22;
  s99.status[t5] = 4;
  let i9 = s99.computeSlot(s99, s99.config.dynamicSlots[t5]);
  return s99.status[t5] = 2 | i9;
}
function ie(s99, e4) {
  return e4 & 1 ? s99.config.staticValues[e4 >> 1] : s99.values[e4 >> 1];
}
var Ne = y.define();
var De = y.define({
  combine: (s99) => s99.some((e4) => e4),
  static: true
});
var Ve = y.define({
  combine: (s99) => s99.length ? s99[0] : void 0,
  static: true
});
var qe = y.define();
var $e = y.define();
var ze = y.define();
var We = y.define({
  combine: (s99) => s99.length ? s99[0] : false
});
var F = class {
  constructor(e4, t5) {
    this.type = e4, this.value = t5;
  }
  static define() {
    return new ge();
  }
};
var ge = class {
  of(e4) {
    return new F(this, e4);
  }
};
var pe = class {
  constructor(e4) {
    this.map = e4;
  }
  of(e4) {
    return new v(this, e4);
  }
};
var v = class s12 {
  constructor(e4, t5) {
    this.type = e4, this.value = t5;
  }
  map(e4) {
    let t5 = this.type.map(this.value, e4);
    return t5 === void 0 ? void 0 : t5 == this.value ? this : new s12(this.type, t5);
  }
  is(e4) {
    return this.type == e4;
  }
  static define(e4 = {}) {
    return new pe(e4.map || ((t5) => t5));
  }
  static mapEffects(e4, t5) {
    if (!e4.length) return e4;
    let n22 = [];
    for (let i9 of e4) {
      let r2 = i9.map(t5);
      r2 && n22.push(r2);
    }
    return n22;
  }
};
v.reconfigure = v.define();
v.appendConfig = v.define();
var S = class s13 {
  constructor(e4, t5, n22, i9, r2, l11) {
    this.startState = e4, this.changes = t5, this.selection = n22, this.effects = i9, this.annotations = r2, this.scrollIntoView = l11, this._doc = null, this._state = null, n22 && Le(n22, t5.newLength), r2.some((h3) => h3.type == s13.time) || (this.annotations = r2.concat(s13.time.of(Date.now())));
  }
  static create(e4, t5, n22, i9, r2, l11) {
    return new s13(e4, t5, n22, i9, r2, l11);
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
  annotation(e4) {
    for (let t5 of this.annotations) if (t5.type == e4) return t5.value;
  }
  get docChanged() {
    return !this.changes.empty;
  }
  get reconfigured() {
    return this.startState.config != this.state.config;
  }
  isUserEvent(e4) {
    let t5 = this.annotation(s13.userEvent);
    return !!(t5 && (t5 == e4 || t5.length > e4.length && t5.slice(0, e4.length) == e4 && t5[e4.length] == "."));
  }
};
S.time = F.define();
S.userEvent = F.define();
S.addToHistory = F.define();
S.remote = F.define();
function Xe(s99, e4) {
  let t5 = [];
  for (let n22 = 0, i9 = 0; ; ) {
    let r2, l11;
    if (n22 < s99.length && (i9 == e4.length || e4[i9] >= s99[n22])) r2 = s99[n22++], l11 = s99[n22++];
    else if (i9 < e4.length) r2 = e4[i9++], l11 = e4[i9++];
    else return t5;
    !t5.length || t5[t5.length - 1] < r2 ? t5.push(r2, l11) : t5[t5.length - 1] < l11 && (t5[t5.length - 1] = l11);
  }
}
function Ue(s99, e4, t5) {
  var n22;
  let i9, r2, l11;
  return t5 ? (i9 = e4.changes, r2 = P.empty(e4.changes.length), l11 = s99.changes.compose(e4.changes)) : (i9 = e4.changes.map(s99.changes), r2 = s99.changes.mapDesc(e4.changes, true), l11 = s99.changes.compose(i9)), {
    changes: l11,
    selection: e4.selection ? e4.selection.map(r2) : (n22 = s99.selection) === null || n22 === void 0 ? void 0 : n22.map(i9),
    effects: v.mapEffects(s99.effects, i9).concat(v.mapEffects(e4.effects, r2)),
    annotations: s99.annotations.length ? s99.annotations.concat(e4.annotations) : e4.annotations,
    scrollIntoView: s99.scrollIntoView || e4.scrollIntoView
  };
}
function me(s99, e4, t5) {
  let n22 = e4.selection, i9 = q(e4.annotations);
  return e4.userEvent && (i9 = i9.concat(S.userEvent.of(e4.userEvent))), {
    changes: e4.changes instanceof P ? e4.changes : P.of(e4.changes || [], t5, s99.facet(Ve)),
    selection: n22 && (n22 instanceof x ? n22 : x.single(n22.anchor, n22.head)),
    effects: q(e4.effects),
    annotations: i9,
    scrollIntoView: !!e4.scrollIntoView
  };
}
function Ge(s99, e4, t5) {
  let n22 = me(s99, e4.length ? e4[0] : {}, s99.doc.length);
  e4.length && e4[0].filter === false && (t5 = false);
  for (let r2 = 1; r2 < e4.length; r2++) {
    e4[r2].filter === false && (t5 = false);
    let l11 = !!e4[r2].sequential;
    n22 = Ue(n22, me(s99, e4[r2], l11 ? n22.changes.newLength : s99.doc.length), l11);
  }
  let i9 = S.create(s99, n22.changes, n22.selection, n22.effects, n22.annotations, n22.scrollIntoView);
  return _e(t5 ? Ye(i9) : i9);
}
function Ye(s99) {
  let e4 = s99.startState, t5 = true;
  for (let i9 of e4.facet(qe)) {
    let r2 = i9(s99);
    if (r2 === false) {
      t5 = false;
      break;
    }
    Array.isArray(r2) && (t5 = t5 === true ? r2 : Xe(t5, r2));
  }
  if (t5 !== true) {
    let i9, r2;
    if (t5 === false) r2 = s99.changes.invertedDesc, i9 = P.empty(e4.doc.length);
    else {
      let l11 = s99.changes.filter(t5);
      i9 = l11.changes, r2 = l11.filtered.invertedDesc;
    }
    s99 = S.create(e4, i9, s99.selection && s99.selection.map(r2), v.mapEffects(s99.effects, r2), s99.annotations, s99.scrollIntoView);
  }
  let n22 = e4.facet($e);
  for (let i9 = n22.length - 1; i9 >= 0; i9--) {
    let r2 = n22[i9](s99);
    r2 instanceof S ? s99 = r2 : Array.isArray(r2) && r2.length == 1 && r2[0] instanceof S ? s99 = r2[0] : s99 = Ge(e4, q(r2), false);
  }
  return s99;
}
function _e(s99) {
  let e4 = s99.startState, t5 = e4.facet(ze), n22 = s99;
  for (let i9 = t5.length - 1; i9 >= 0; i9--) {
    let r2 = t5[i9](s99);
    r2 && Object.keys(r2).length && (n22 = Ue(s99, me(e4, r2, s99.changes.newLength), true));
  }
  return n22 == s99 ? s99 : S.create(e4, s99.changes, s99.selection, n22.effects, n22.annotations, n22.scrollIntoView);
}
var et = [];
function q(s99) {
  return s99 == null ? et : Array.isArray(s99) ? s99 : [
    s99
  ];
}
var E = function(s99) {
  return s99[s99.Word = 0] = "Word", s99[s99.Space = 1] = "Space", s99[s99.Other = 2] = "Other", s99;
}(E || (E = {}));
var tt = /[\u00df\u0587\u0590-\u05f4\u0600-\u06ff\u3040-\u309f\u30a0-\u30ff\u3400-\u4db5\u4e00-\u9fcc\uac00-\ud7af]/;
var we;
try {
  we = new RegExp("[\\p{Alphabetic}\\p{Number}_]", "u");
} catch {
}
function nt(s99) {
  if (we) return we.test(s99);
  for (let e4 = 0; e4 < s99.length; e4++) {
    let t5 = s99[e4];
    if (/\w/.test(t5) || t5 > "\x80" && (t5.toUpperCase() != t5.toLowerCase() || tt.test(t5))) return true;
  }
  return false;
}
function it(s99) {
  return (e4) => {
    if (!/\S/.test(e4)) return E.Space;
    if (nt(e4)) return E.Word;
    for (let t5 = 0; t5 < s99.length; t5++) if (e4.indexOf(s99[t5]) > -1) return E.Word;
    return E.Other;
  };
}
var I = class s14 {
  constructor(e4, t5, n22, i9, r2, l11) {
    this.config = e4, this.doc = t5, this.selection = n22, this.values = i9, this.status = e4.statusTemplate.slice(), this.computeSlot = r2, l11 && (l11._state = this);
    for (let h3 = 0; h3 < this.config.dynamicSlots.length; h3++) U(this, h3 << 1);
    this.computeSlot = null;
  }
  field(e4, t5 = true) {
    let n22 = this.config.address[e4.id];
    if (n22 == null) {
      if (t5) throw new RangeError("Field is not present in this state");
      return;
    }
    return U(this, n22), ie(this, n22);
  }
  update(...e4) {
    return Ge(this, e4, true);
  }
  applyTransaction(e4) {
    let t5 = this.config, { base: n22, compartments: i9 } = t5;
    for (let l11 of e4.effects) l11.is(te.reconfigure) ? (t5 && (i9 = /* @__PURE__ */ new Map(), t5.compartments.forEach((h3, o4) => i9.set(o4, h3)), t5 = null), i9.set(l11.value.compartment, l11.value.extension)) : l11.is(v.reconfigure) ? (t5 = null, n22 = l11.value) : l11.is(v.appendConfig) && (t5 = null, n22 = q(n22).concat(l11.value));
    let r2;
    t5 ? r2 = e4.startState.values.slice() : (t5 = ne.resolve(n22, i9, this), r2 = new s14(t5, this.doc, this.selection, t5.dynamicSlots.map(() => null), (h3, o4) => o4.reconfigure(h3, this), null).values), new s14(t5, e4.newDoc, e4.newSelection, r2, (l11, h3) => h3.update(l11, e4), e4);
  }
  replaceSelection(e4) {
    return typeof e4 == "string" && (e4 = this.toText(e4)), this.changeByRange((t5) => ({
      changes: {
        from: t5.from,
        to: t5.to,
        insert: e4
      },
      range: x.cursor(t5.from + e4.length)
    }));
  }
  changeByRange(e4) {
    let t5 = this.selection, n22 = e4(t5.ranges[0]), i9 = this.changes(n22.changes), r2 = [
      n22.range
    ], l11 = q(n22.effects);
    for (let h3 = 1; h3 < t5.ranges.length; h3++) {
      let o4 = e4(t5.ranges[h3]), a2 = this.changes(o4.changes), f2 = a2.map(i9);
      for (let c4 = 0; c4 < h3; c4++) r2[c4] = r2[c4].map(f2);
      let u5 = i9.mapDesc(a2, true);
      r2.push(o4.range.map(u5)), i9 = i9.compose(f2), l11 = v.mapEffects(l11, f2).concat(v.mapEffects(q(o4.effects), u5));
    }
    return {
      changes: i9,
      selection: x.create(r2, t5.mainIndex),
      effects: l11
    };
  }
  changes(e4 = []) {
    return e4 instanceof P ? e4 : P.of(e4, this.doc.length, this.facet(s14.lineSeparator));
  }
  toText(e4) {
    return m.of(e4.split(this.facet(s14.lineSeparator) || fe));
  }
  sliceDoc(e4 = 0, t5 = this.doc.length) {
    return this.doc.sliceString(e4, t5, this.lineBreak);
  }
  facet(e4) {
    let t5 = this.config.address[e4.id];
    return t5 == null ? e4.default : (U(this, t5), ie(this, t5));
  }
  toJSON(e4) {
    let t5 = {
      doc: this.sliceDoc(),
      selection: this.selection.toJSON()
    };
    if (e4) for (let n22 in e4) {
      let i9 = e4[n22];
      i9 instanceof $ && (t5[n22] = i9.spec.toJSON(this.field(e4[n22]), this));
    }
    return t5;
  }
  static fromJSON(e4, t5 = {}, n22) {
    if (!e4 || typeof e4.doc != "string") throw new RangeError("Invalid JSON representation for EditorState");
    let i9 = [];
    if (n22) for (let r2 in n22) {
      let l11 = n22[r2], h3 = e4[r2];
      i9.push(l11.init((o4) => l11.spec.fromJSON(h3, o4)));
    }
    return s14.create({
      doc: e4.doc,
      selection: x.fromJSON(e4.selection),
      extensions: t5.extensions ? i9.concat([
        t5.extensions
      ]) : i9
    });
  }
  static create(e4 = {}) {
    let t5 = ne.resolve(e4.extensions || [], /* @__PURE__ */ new Map()), n22 = e4.doc instanceof m ? e4.doc : m.of((e4.doc || "").split(t5.staticFacet(s14.lineSeparator) || fe)), i9 = e4.selection ? e4.selection instanceof x ? e4.selection : x.single(e4.selection.anchor, e4.selection.head) : x.single(0);
    return Le(i9, n22.length), t5.staticFacet(De) || (i9 = i9.asSingle()), new s14(t5, n22, i9, t5.dynamicSlots.map(() => null), (r2, l11) => l11.create(r2), null);
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
  phrase(e4, ...t5) {
    for (let n22 of this.facet(s14.phrases)) if (Object.prototype.hasOwnProperty.call(n22, e4)) {
      e4 = n22[e4];
      break;
    }
    return t5.length && (e4 = e4.replace(/\$(\$|\d*)/g, (n22, i9) => {
      if (i9 == "$") return "$";
      let r2 = +(i9 || 1);
      return r2 > t5.length ? n22 : t5[r2 - 1];
    })), e4;
  }
  languageDataAt(e4, t5, n22 = -1) {
    let i9 = [];
    for (let r2 of this.facet(Ne)) for (let l11 of r2(this, t5, n22)) Object.prototype.hasOwnProperty.call(l11, e4) && i9.push(l11[e4]);
    return i9;
  }
  charCategorizer(e4) {
    return it(this.languageDataAt("wordChars", e4).join(""));
  }
  wordAt(e4) {
    let { text: t5, from: n22, length: i9 } = this.doc.lineAt(e4), r2 = this.charCategorizer(e4), l11 = e4 - n22, h3 = e4 - n22;
    for (; l11 > 0; ) {
      let o4 = _(t5, l11, false);
      if (r2(t5.slice(o4, l11)) != E.Word) break;
      l11 = o4;
    }
    for (; h3 < i9; ) {
      let o4 = _(t5, h3);
      if (r2(t5.slice(h3, o4)) != E.Word) break;
      h3 = o4;
    }
    return l11 == h3 ? null : x.range(l11 + n22, h3 + n22);
  }
};
I.allowMultipleSelections = De;
I.tabSize = y.define({
  combine: (s99) => s99.length ? s99[0] : 4
});
I.lineSeparator = Ve;
I.readOnly = We;
I.phrases = y.define({
  compare(s99, e4) {
    let t5 = Object.keys(s99), n22 = Object.keys(e4);
    return t5.length == n22.length && t5.every((i9) => s99[i9] == e4[i9]);
  }
});
I.languageData = Ne;
I.changeFilter = qe;
I.transactionFilter = $e;
I.transactionExtender = ze;
te.reconfigure = v.define();
function ht(s99, e4, t5 = {}) {
  let n22 = {};
  for (let i9 of s99) for (let r2 of Object.keys(i9)) {
    let l11 = i9[r2], h3 = n22[r2];
    if (h3 === void 0) n22[r2] = l11;
    else if (!(h3 === l11 || l11 === void 0)) if (Object.hasOwnProperty.call(t5, r2)) n22[r2] = t5[r2](h3, l11);
    else throw new Error("Config merge conflict for field " + r2);
  }
  for (let i9 in e4) n22[i9] === void 0 && (n22[i9] = e4[i9]);
  return n22;
}
var z = class {
  eq(e4) {
    return this == e4;
  }
  range(e4, t5 = e4) {
    return j.create(e4, t5, this);
  }
};
z.prototype.startSide = z.prototype.endSide = 0;
z.prototype.point = false;
z.prototype.mapMode = b.TrackDel;
var j = class s15 {
  constructor(e4, t5, n22) {
    this.from = e4, this.to = t5, this.value = n22;
  }
  static create(e4, t5, n22) {
    return new s15(e4, t5, n22);
  }
};
function ve(s99, e4) {
  return s99.from - e4.from || s99.value.startSide - e4.value.startSide;
}
var xe = class s16 {
  constructor(e4, t5, n22, i9) {
    this.from = e4, this.to = t5, this.value = n22, this.maxPoint = i9;
  }
  get length() {
    return this.to[this.to.length - 1];
  }
  findIndex(e4, t5, n22, i9 = 0) {
    let r2 = n22 ? this.to : this.from;
    for (let l11 = i9, h3 = r2.length; ; ) {
      if (l11 == h3) return l11;
      let o4 = l11 + h3 >> 1, a2 = r2[o4] - e4 || (n22 ? this.value[o4].endSide : this.value[o4].startSide) - t5;
      if (o4 == l11) return a2 >= 0 ? l11 : h3;
      a2 >= 0 ? h3 = o4 : l11 = o4 + 1;
    }
  }
  between(e4, t5, n22, i9) {
    for (let r2 = this.findIndex(t5, -1e9, true), l11 = this.findIndex(n22, 1e9, false, r2); r2 < l11; r2++) if (i9(this.from[r2] + e4, this.to[r2] + e4, this.value[r2]) === false) return false;
  }
  map(e4, t5) {
    let n22 = [], i9 = [], r2 = [], l11 = -1, h3 = -1;
    for (let o4 = 0; o4 < this.value.length; o4++) {
      let a2 = this.value[o4], f2 = this.from[o4] + e4, u5 = this.to[o4] + e4, c4, d5;
      if (f2 == u5) {
        let g6 = t5.mapPos(f2, a2.startSide, a2.mapMode);
        if (g6 == null || (c4 = d5 = g6, a2.startSide != a2.endSide && (d5 = t5.mapPos(f2, a2.endSide), d5 < c4))) continue;
      } else if (c4 = t5.mapPos(f2, a2.startSide), d5 = t5.mapPos(u5, a2.endSide), c4 > d5 || c4 == d5 && a2.startSide > 0 && a2.endSide <= 0) continue;
      (d5 - c4 || a2.endSide - a2.startSide) < 0 || (l11 < 0 && (l11 = c4), a2.point && (h3 = Math.max(h3, d5 - c4)), n22.push(a2), i9.push(c4 - l11), r2.push(d5 - l11));
    }
    return {
      mapped: n22.length ? new s16(i9, r2, n22, h3) : null,
      pos: l11
    };
  }
};
var O = class s17 {
  constructor(e4, t5, n22, i9) {
    this.chunkPos = e4, this.chunk = t5, this.nextLayer = n22, this.maxPoint = i9;
  }
  static create(e4, t5, n22, i9) {
    return new s17(e4, t5, n22, i9);
  }
  get length() {
    let e4 = this.chunk.length - 1;
    return e4 < 0 ? 0 : Math.max(this.chunkEnd(e4), this.nextLayer.length);
  }
  get size() {
    if (this.isEmpty) return 0;
    let e4 = this.nextLayer.size;
    for (let t5 of this.chunk) e4 += t5.value.length;
    return e4;
  }
  chunkEnd(e4) {
    return this.chunkPos[e4] + this.chunk[e4].length;
  }
  update(e4) {
    let { add: t5 = [], sort: n22 = false, filterFrom: i9 = 0, filterTo: r2 = this.length } = e4, l11 = e4.filter;
    if (t5.length == 0 && !l11) return this;
    if (n22 && (t5 = t5.slice().sort(ve)), this.isEmpty) return t5.length ? s17.of(t5) : this;
    let h3 = new re(this, null, -1).goto(0), o4 = 0, a2 = [], f2 = new se();
    for (; h3.value || o4 < t5.length; ) if (o4 < t5.length && (h3.from - t5[o4].from || h3.startSide - t5[o4].value.startSide) >= 0) {
      let u5 = t5[o4++];
      f2.addInner(u5.from, u5.to, u5.value) || a2.push(u5);
    } else h3.rangeIndex == 1 && h3.chunkIndex < this.chunk.length && (o4 == t5.length || this.chunkEnd(h3.chunkIndex) < t5[o4].from) && (!l11 || i9 > this.chunkEnd(h3.chunkIndex) || r2 < this.chunkPos[h3.chunkIndex]) && f2.addChunk(this.chunkPos[h3.chunkIndex], this.chunk[h3.chunkIndex]) ? h3.nextChunk() : ((!l11 || i9 > h3.to || r2 < h3.from || l11(h3.from, h3.to, h3.value)) && (f2.addInner(h3.from, h3.to, h3.value) || a2.push(j.create(h3.from, h3.to, h3.value))), h3.next());
    return f2.finishInner(this.nextLayer.isEmpty && !a2.length ? s17.empty : this.nextLayer.update({
      add: a2,
      filter: l11,
      filterFrom: i9,
      filterTo: r2
    }));
  }
  map(e4) {
    if (e4.empty || this.isEmpty) return this;
    let t5 = [], n22 = [], i9 = -1;
    for (let l11 = 0; l11 < this.chunk.length; l11++) {
      let h3 = this.chunkPos[l11], o4 = this.chunk[l11], a2 = e4.touchesRange(h3, h3 + o4.length);
      if (a2 === false) i9 = Math.max(i9, o4.maxPoint), t5.push(o4), n22.push(e4.mapPos(h3));
      else if (a2 === true) {
        let { mapped: f2, pos: u5 } = o4.map(h3, e4);
        f2 && (i9 = Math.max(i9, f2.maxPoint), t5.push(f2), n22.push(u5));
      }
    }
    let r2 = this.nextLayer.map(e4);
    return t5.length == 0 ? r2 : new s17(n22, t5, r2 || s17.empty, i9);
  }
  between(e4, t5, n22) {
    if (!this.isEmpty) {
      for (let i9 = 0; i9 < this.chunk.length; i9++) {
        let r2 = this.chunkPos[i9], l11 = this.chunk[i9];
        if (t5 >= r2 && e4 <= r2 + l11.length && l11.between(r2, e4 - r2, t5 - r2, n22) === false) return;
      }
      this.nextLayer.between(e4, t5, n22);
    }
  }
  iter(e4 = 0) {
    return H.from([
      this
    ]).goto(e4);
  }
  get isEmpty() {
    return this.nextLayer == this;
  }
  static iter(e4, t5 = 0) {
    return H.from(e4).goto(t5);
  }
  static compare(e4, t5, n22, i9, r2 = -1) {
    let l11 = e4.filter((u5) => u5.maxPoint > 0 || !u5.isEmpty && u5.maxPoint >= r2), h3 = t5.filter((u5) => u5.maxPoint > 0 || !u5.isEmpty && u5.maxPoint >= r2), o4 = Te(l11, h3, n22), a2 = new T(l11, o4, r2), f2 = new T(h3, o4, r2);
    n22.iterGaps((u5, c4, d5) => Re(a2, u5, f2, c4, d5, i9)), n22.empty && n22.length == 0 && Re(a2, 0, f2, 0, 0, i9);
  }
  static eq(e4, t5, n22 = 0, i9) {
    i9 == null && (i9 = 1e9);
    let r2 = e4.filter((f2) => !f2.isEmpty && t5.indexOf(f2) < 0), l11 = t5.filter((f2) => !f2.isEmpty && e4.indexOf(f2) < 0);
    if (r2.length != l11.length) return false;
    if (!r2.length) return true;
    let h3 = Te(r2, l11), o4 = new T(r2, h3, 0).goto(n22), a2 = new T(l11, h3, 0).goto(n22);
    for (; ; ) {
      if (o4.to != a2.to || !ke(o4.active, a2.active) || o4.point && (!a2.point || !o4.point.eq(a2.point))) return false;
      if (o4.to > i9) return true;
      o4.next(), a2.next();
    }
  }
  static spans(e4, t5, n22, i9, r2 = -1) {
    let l11 = new T(e4, null, r2).goto(t5), h3 = t5, o4 = l11.openStart;
    for (; ; ) {
      let a2 = Math.min(l11.to, n22);
      if (l11.point ? (i9.point(h3, a2, l11.point, l11.activeForPoint(l11.to), o4, l11.pointRank), o4 = l11.openEnd(a2) + (l11.to > a2 ? 1 : 0)) : a2 > h3 && (i9.span(h3, a2, l11.active, o4), o4 = l11.openEnd(a2)), l11.to > n22) break;
      h3 = l11.to, l11.next();
    }
    return o4;
  }
  static of(e4, t5 = false) {
    let n22 = new se();
    for (let i9 of e4 instanceof j ? [
      e4
    ] : t5 ? st(e4) : e4) n22.add(i9.from, i9.to, i9.value);
    return n22.finish();
  }
};
O.empty = new O([], [], null, -1);
function st(s99) {
  if (s99.length > 1) for (let e4 = s99[0], t5 = 1; t5 < s99.length; t5++) {
    let n22 = s99[t5];
    if (ve(e4, n22) > 0) return s99.slice().sort(ve);
    e4 = n22;
  }
  return s99;
}
O.empty.nextLayer = O.empty;
var se = class s18 {
  constructor() {
    this.chunks = [], this.chunkPos = [], this.chunkStart = -1, this.last = null, this.lastFrom = -1e9, this.lastTo = -1e9, this.from = [], this.to = [], this.value = [], this.maxPoint = -1, this.setMaxPoint = -1, this.nextLayer = null;
  }
  finishChunk(e4) {
    this.chunks.push(new xe(this.from, this.to, this.value, this.maxPoint)), this.chunkPos.push(this.chunkStart), this.chunkStart = -1, this.setMaxPoint = Math.max(this.setMaxPoint, this.maxPoint), this.maxPoint = -1, e4 && (this.from = [], this.to = [], this.value = []);
  }
  add(e4, t5, n22) {
    this.addInner(e4, t5, n22) || (this.nextLayer || (this.nextLayer = new s18())).add(e4, t5, n22);
  }
  addInner(e4, t5, n22) {
    let i9 = e4 - this.lastTo || n22.startSide - this.last.endSide;
    if (i9 <= 0 && (e4 - this.lastFrom || n22.startSide - this.last.startSide) < 0) throw new Error("Ranges must be added sorted by `from` position and `startSide`");
    return i9 < 0 ? false : (this.from.length == 250 && this.finishChunk(true), this.chunkStart < 0 && (this.chunkStart = e4), this.from.push(e4 - this.chunkStart), this.to.push(t5 - this.chunkStart), this.last = n22, this.lastFrom = e4, this.lastTo = t5, this.value.push(n22), n22.point && (this.maxPoint = Math.max(this.maxPoint, t5 - e4)), true);
  }
  addChunk(e4, t5) {
    if ((e4 - this.lastTo || t5.value[0].startSide - this.last.endSide) < 0) return false;
    this.from.length && this.finishChunk(true), this.setMaxPoint = Math.max(this.setMaxPoint, t5.maxPoint), this.chunks.push(t5), this.chunkPos.push(e4);
    let n22 = t5.value.length - 1;
    return this.last = t5.value[n22], this.lastFrom = t5.from[n22] + e4, this.lastTo = t5.to[n22] + e4, true;
  }
  finish() {
    return this.finishInner(O.empty);
  }
  finishInner(e4) {
    if (this.from.length && this.finishChunk(false), this.chunks.length == 0) return e4;
    let t5 = O.create(this.chunkPos, this.chunks, this.nextLayer ? this.nextLayer.finishInner(e4) : e4, this.setMaxPoint);
    return this.from = null, t5;
  }
};
function Te(s99, e4, t5) {
  let n22 = /* @__PURE__ */ new Map();
  for (let r2 of s99) for (let l11 = 0; l11 < r2.chunk.length; l11++) r2.chunk[l11].maxPoint <= 0 && n22.set(r2.chunk[l11], r2.chunkPos[l11]);
  let i9 = /* @__PURE__ */ new Set();
  for (let r2 of e4) for (let l11 = 0; l11 < r2.chunk.length; l11++) {
    let h3 = n22.get(r2.chunk[l11]);
    h3 != null && (t5 ? t5.mapPos(h3) : h3) == r2.chunkPos[l11] && !t5?.touchesRange(h3, h3 + r2.chunk[l11].length) && i9.add(r2.chunk[l11]);
  }
  return i9;
}
var re = class {
  constructor(e4, t5, n22, i9 = 0) {
    this.layer = e4, this.skip = t5, this.minPoint = n22, this.rank = i9;
  }
  get startSide() {
    return this.value ? this.value.startSide : 0;
  }
  get endSide() {
    return this.value ? this.value.endSide : 0;
  }
  goto(e4, t5 = -1e9) {
    return this.chunkIndex = this.rangeIndex = 0, this.gotoInner(e4, t5, false), this;
  }
  gotoInner(e4, t5, n22) {
    for (; this.chunkIndex < this.layer.chunk.length; ) {
      let i9 = this.layer.chunk[this.chunkIndex];
      if (!(this.skip && this.skip.has(i9) || this.layer.chunkEnd(this.chunkIndex) < e4 || i9.maxPoint < this.minPoint)) break;
      this.chunkIndex++, n22 = false;
    }
    if (this.chunkIndex < this.layer.chunk.length) {
      let i9 = this.layer.chunk[this.chunkIndex].findIndex(e4 - this.layer.chunkPos[this.chunkIndex], t5, true);
      (!n22 || this.rangeIndex < i9) && this.setRangeIndex(i9);
    }
    this.next();
  }
  forward(e4, t5) {
    (this.to - e4 || this.endSide - t5) < 0 && this.gotoInner(e4, t5, true);
  }
  next() {
    for (; ; ) if (this.chunkIndex == this.layer.chunk.length) {
      this.from = this.to = 1e9, this.value = null;
      break;
    } else {
      let e4 = this.layer.chunkPos[this.chunkIndex], t5 = this.layer.chunk[this.chunkIndex], n22 = e4 + t5.from[this.rangeIndex];
      if (this.from = n22, this.to = e4 + t5.to[this.rangeIndex], this.value = t5.value[this.rangeIndex], this.setRangeIndex(this.rangeIndex + 1), this.minPoint < 0 || this.value.point && this.to - this.from >= this.minPoint) break;
    }
  }
  setRangeIndex(e4) {
    if (e4 == this.layer.chunk[this.chunkIndex].value.length) {
      if (this.chunkIndex++, this.skip) for (; this.chunkIndex < this.layer.chunk.length && this.skip.has(this.layer.chunk[this.chunkIndex]); ) this.chunkIndex++;
      this.rangeIndex = 0;
    } else this.rangeIndex = e4;
  }
  nextChunk() {
    this.chunkIndex++, this.rangeIndex = 0, this.next();
  }
  compare(e4) {
    return this.from - e4.from || this.startSide - e4.startSide || this.rank - e4.rank || this.to - e4.to || this.endSide - e4.endSide;
  }
};
var H = class s19 {
  constructor(e4) {
    this.heap = e4;
  }
  static from(e4, t5 = null, n22 = -1) {
    let i9 = [];
    for (let r2 = 0; r2 < e4.length; r2++) for (let l11 = e4[r2]; !l11.isEmpty; l11 = l11.nextLayer) l11.maxPoint >= n22 && i9.push(new re(l11, t5, n22, r2));
    return i9.length == 1 ? i9[0] : new s19(i9);
  }
  get startSide() {
    return this.value ? this.value.startSide : 0;
  }
  goto(e4, t5 = -1e9) {
    for (let n22 of this.heap) n22.goto(e4, t5);
    for (let n22 = this.heap.length >> 1; n22 >= 0; n22--) oe(this.heap, n22);
    return this.next(), this;
  }
  forward(e4, t5) {
    for (let n22 of this.heap) n22.forward(e4, t5);
    for (let n22 = this.heap.length >> 1; n22 >= 0; n22--) oe(this.heap, n22);
    (this.to - e4 || this.value.endSide - t5) < 0 && this.next();
  }
  next() {
    if (this.heap.length == 0) this.from = this.to = 1e9, this.value = null, this.rank = -1;
    else {
      let e4 = this.heap[0];
      this.from = e4.from, this.to = e4.to, this.value = e4.value, this.rank = e4.rank, e4.value && e4.next(), oe(this.heap, 0);
    }
  }
};
function oe(s99, e4) {
  for (let t5 = s99[e4]; ; ) {
    let n22 = (e4 << 1) + 1;
    if (n22 >= s99.length) break;
    let i9 = s99[n22];
    if (n22 + 1 < s99.length && i9.compare(s99[n22 + 1]) >= 0 && (i9 = s99[n22 + 1], n22++), t5.compare(i9) < 0) break;
    s99[n22] = t5, s99[e4] = i9, e4 = n22;
  }
}
var T = class {
  constructor(e4, t5, n22) {
    this.minPoint = n22, this.active = [], this.activeTo = [], this.activeRank = [], this.minActive = -1, this.point = null, this.pointFrom = 0, this.pointRank = 0, this.to = -1e9, this.endSide = 0, this.openStart = -1, this.cursor = H.from(e4, t5, n22);
  }
  goto(e4, t5 = -1e9) {
    return this.cursor.goto(e4, t5), this.active.length = this.activeTo.length = this.activeRank.length = 0, this.minActive = -1, this.to = e4, this.endSide = t5, this.openStart = -1, this.next(), this;
  }
  forward(e4, t5) {
    for (; this.minActive > -1 && (this.activeTo[this.minActive] - e4 || this.active[this.minActive].endSide - t5) < 0; ) this.removeActive(this.minActive);
    this.cursor.forward(e4, t5);
  }
  removeActive(e4) {
    Z(this.active, e4), Z(this.activeTo, e4), Z(this.activeRank, e4), this.minActive = Be(this.active, this.activeTo);
  }
  addActive(e4) {
    let t5 = 0, { value: n22, to: i9, rank: r2 } = this.cursor;
    for (; t5 < this.activeRank.length && this.activeRank[t5] <= r2; ) t5++;
    K(this.active, t5, n22), K(this.activeTo, t5, i9), K(this.activeRank, t5, r2), e4 && K(e4, t5, this.cursor.from), this.minActive = Be(this.active, this.activeTo);
  }
  next() {
    let e4 = this.to, t5 = this.point;
    this.point = null;
    let n22 = this.openStart < 0 ? [] : null, i9 = 0;
    for (; ; ) {
      let r2 = this.minActive;
      if (r2 > -1 && (this.activeTo[r2] - this.cursor.from || this.active[r2].endSide - this.cursor.startSide) < 0) {
        if (this.activeTo[r2] > e4) {
          this.to = this.activeTo[r2], this.endSide = this.active[r2].endSide;
          break;
        }
        this.removeActive(r2), n22 && Z(n22, r2);
      } else if (this.cursor.value) if (this.cursor.from > e4) {
        this.to = this.cursor.from, this.endSide = this.cursor.startSide;
        break;
      } else {
        let l11 = this.cursor.value;
        if (!l11.point) this.addActive(n22), this.cursor.next();
        else if (t5 && this.cursor.to == this.to && this.cursor.from < this.cursor.to) this.cursor.next();
        else {
          this.point = l11, this.pointFrom = this.cursor.from, this.pointRank = this.cursor.rank, this.to = this.cursor.to, this.endSide = l11.endSide, this.cursor.from < e4 && (i9 = 1), this.cursor.next(), this.forward(this.to, this.endSide);
          break;
        }
      }
      else {
        this.to = this.endSide = 1e9;
        break;
      }
    }
    if (n22) {
      let r2 = 0;
      for (; r2 < n22.length && n22[r2] < e4; ) r2++;
      this.openStart = r2 + i9;
    }
  }
  activeForPoint(e4) {
    if (!this.active.length) return this.active;
    let t5 = [];
    for (let n22 = this.active.length - 1; n22 >= 0 && !(this.activeRank[n22] < this.pointRank); n22--) (this.activeTo[n22] > e4 || this.activeTo[n22] == e4 && this.active[n22].endSide >= this.point.endSide) && t5.push(this.active[n22]);
    return t5.reverse();
  }
  openEnd(e4) {
    let t5 = 0;
    for (let n22 = this.activeTo.length - 1; n22 >= 0 && this.activeTo[n22] > e4; n22--) t5++;
    return t5;
  }
};
function Re(s99, e4, t5, n22, i9, r2) {
  s99.goto(e4), t5.goto(n22);
  let l11 = n22 + i9, h3 = n22, o4 = n22 - e4;
  for (; ; ) {
    let a2 = s99.to + o4 - t5.to || s99.endSide - t5.endSide, f2 = a2 < 0 ? s99.to + o4 : t5.to, u5 = Math.min(f2, l11);
    if (s99.point || t5.point ? s99.point && t5.point && (s99.point == t5.point || s99.point.eq(t5.point)) && ke(s99.activeForPoint(s99.to + o4), t5.activeForPoint(t5.to)) || r2.comparePoint(h3, u5, s99.point, t5.point) : u5 > h3 && !ke(s99.active, t5.active) && r2.compareRange(h3, u5, s99.active, t5.active), f2 > l11) break;
    h3 = f2, a2 <= 0 && s99.next(), a2 >= 0 && t5.next();
  }
}
function ke(s99, e4) {
  if (s99.length != e4.length) return false;
  for (let t5 = 0; t5 < s99.length; t5++) if (s99[t5] != e4[t5] && !s99[t5].eq(e4[t5])) return false;
  return true;
}
function Z(s99, e4) {
  for (let t5 = e4, n22 = s99.length - 1; t5 < n22; t5++) s99[t5] = s99[t5 + 1];
  s99.pop();
}
function K(s99, e4, t5) {
  for (let n22 = s99.length - 1; n22 >= e4; n22--) s99[n22 + 1] = s99[n22];
  s99[e4] = t5;
}
function Be(s99, e4) {
  let t5 = -1, n22 = 1e9;
  for (let i9 = 0; i9 < e4.length; i9++) (e4[i9] - n22 || s99[i9].endSide - s99[t5].endSide) < 0 && (t5 = i9, n22 = e4[i9]);
  return t5;
}
function ot(s99, e4, t5 = s99.length) {
  let n22 = 0;
  for (let i9 = 0; i9 < t5; ) s99.charCodeAt(i9) == 9 ? (n22 += e4 - n22 % e4, i9++) : (n22++, i9 = _(s99, i9));
  return n22;
}
function at(s99, e4, t5, n22) {
  for (let i9 = 0, r2 = 0; ; ) {
    if (r2 >= e4) return i9;
    if (i9 == s99.length) break;
    r2 += s99.charCodeAt(i9) == 9 ? t5 - r2 % t5 : 1, i9 = _(s99, i9);
  }
  return n22 === true ? -1 : s99.length;
}

// deno:https://esm.sh/style-mod@4.1.3/denonext/style-mod.mjs
var m2 = typeof Symbol > "u" ? "__\u037C" : Symbol.for("\u037C");
var c = typeof Symbol > "u" ? "__styleSet" + Math.floor(Math.random() * 1e8) : Symbol("styleSet");
var w2 = typeof globalThis < "u" || typeof globalThis < "u" ? globalThis : {};
var T2 = class {
  constructor(e4, i9) {
    this.rules = [];
    let { finish: l11 } = i9 || {};
    function n22(t5) {
      return /^@/.test(t5) ? [
        t5
      ] : t5.split(/,\s*/);
    }
    function s99(t5, a2, h3, f2) {
      let p5 = [], u5 = /^@(\w+)\b/.exec(t5[0]), g6 = u5 && u5[1] == "keyframes";
      if (u5 && a2 == null) return h3.push(t5[0] + ";");
      for (let o4 in a2) {
        let r2 = a2[o4];
        if (/&/.test(o4)) s99(o4.split(/,\s*/).map((d5) => t5.map((y10) => d5.replace(/&/, y10))).reduce((d5, y10) => d5.concat(y10)), r2, h3);
        else if (r2 && typeof r2 == "object") {
          if (!u5) throw new RangeError("The value of a property (" + o4 + ") should be a primitive value.");
          s99(n22(o4), r2, p5, g6);
        } else r2 != null && p5.push(o4.replace(/_.*/, "").replace(/[A-Z]/g, (d5) => "-" + d5.toLowerCase()) + ": " + r2 + ";");
      }
      (p5.length || g6) && h3.push((l11 && !u5 && !f2 ? t5.map(l11) : t5).join(", ") + " {" + p5.join(" ") + "}");
    }
    for (let t5 in e4) s99(n22(t5), e4[t5], this.rules);
  }
  getRules() {
    return this.rules.join(`
`);
  }
  static newName() {
    let e4 = w2[m2] || 1;
    return w2[m2] = e4 + 1, "\u037C" + e4.toString(36);
  }
  static mount(e4, i9, l11) {
    let n22 = e4[c], s99 = l11 && l11.nonce;
    n22 ? s99 && n22.setNonce(s99) : n22 = new S2(e4, s99), n22.mount(Array.isArray(i9) ? i9 : [
      i9
    ], e4);
  }
};
var b2 = /* @__PURE__ */ new Map();
var S2 = class {
  constructor(e4, i9) {
    let l11 = e4.ownerDocument || e4, n22 = l11.defaultView;
    if (!e4.head && e4.adoptedStyleSheets && n22.CSSStyleSheet) {
      let s99 = b2.get(l11);
      if (s99) return e4[c] = s99;
      this.sheet = new n22.CSSStyleSheet(), b2.set(l11, this);
    } else this.styleTag = l11.createElement("style"), i9 && this.styleTag.setAttribute("nonce", i9);
    this.modules = [], e4[c] = this;
  }
  mount(e4, i9) {
    let l11 = this.sheet, n22 = 0, s99 = 0;
    for (let t5 = 0; t5 < e4.length; t5++) {
      let a2 = e4[t5], h3 = this.modules.indexOf(a2);
      if (h3 < s99 && h3 > -1 && (this.modules.splice(h3, 1), s99--, h3 = -1), h3 == -1) {
        if (this.modules.splice(s99++, 0, a2), l11) for (let f2 = 0; f2 < a2.rules.length; f2++) l11.insertRule(a2.rules[f2], n22++);
      } else {
        for (; s99 < h3; ) n22 += this.modules[s99++].rules.length;
        n22 += a2.rules.length, s99++;
      }
    }
    if (l11) i9.adoptedStyleSheets.indexOf(this.sheet) < 0 && (i9.adoptedStyleSheets = [
      this.sheet,
      ...i9.adoptedStyleSheets
    ]);
    else {
      let t5 = "";
      for (let h3 = 0; h3 < this.modules.length; h3++) t5 += this.modules[h3].getRules() + `
`;
      this.styleTag.textContent = t5;
      let a2 = i9.head || i9;
      this.styleTag.parentNode != a2 && a2.insertBefore(this.styleTag, a2.firstChild);
    }
  }
  setNonce(e4) {
    this.styleTag && this.styleTag.getAttribute("nonce") != e4 && this.styleTag.setAttribute("nonce", e4);
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
function g(o4) {
  var f2 = n && o4.metaKey && o4.shiftKey && !o4.ctrlKey && !o4.altKey || y2 && o4.shiftKey && o4.key && o4.key.length == 1 || o4.key == "Unidentified", e4 = !f2 && o4.key || (o4.shiftKey ? i : t)[o4.keyCode] || o4.key || "Unidentified";
  return e4 == "Esc" && (e4 = "Escape"), e4 == "Del" && (e4 = "Delete"), e4 == "Left" && (e4 = "ArrowLeft"), e4 == "Up" && (e4 = "ArrowUp"), e4 == "Right" && (e4 = "ArrowRight"), e4 == "Down" && (e4 = "ArrowDown"), e4;
}

// deno:https://esm.sh/@codemirror/view@0.20.7/denonext/view.mjs
function Yt(s99) {
  let t5;
  return s99.nodeType == 11 ? t5 = s99.getSelection ? s99 : s99.ownerDocument : t5 = s99, t5.getSelection();
}
function pt(s99, t5) {
  return t5 ? s99 == t5 || s99.contains(t5.nodeType != 1 ? t5.parentNode : t5) : false;
}
function gn() {
  let s99 = document.activeElement;
  for (; s99 && s99.shadowRoot; ) s99 = s99.shadowRoot.activeElement;
  return s99;
}
function De2(s99, t5) {
  if (!t5.anchorNode) return false;
  try {
    return pt(s99, t5.anchorNode);
  } catch {
    return false;
  }
}
function Tt(s99) {
  return s99.nodeType == 3 ? Ot(s99, 0, s99.nodeValue.length).getClientRects() : s99.nodeType == 1 ? s99.getClientRects() : [];
}
function Ut(s99, t5, e4, i9) {
  return e4 ? xi(s99, t5, e4, i9, -1) || xi(s99, t5, e4, i9, 1) : false;
}
function Te2(s99) {
  for (var t5 = 0; ; t5++) if (s99 = s99.previousSibling, !s99) return t5;
}
function xi(s99, t5, e4, i9, n22) {
  for (; ; ) {
    if (s99 == e4 && t5 == i9) return true;
    if (t5 == (n22 < 0 ? 0 : Xt(s99))) {
      if (s99.nodeName == "DIV") return false;
      let r2 = s99.parentNode;
      if (!r2 || r2.nodeType != 1) return false;
      t5 = Te2(s99) + (n22 < 0 ? 0 : 1), s99 = r2;
    } else if (s99.nodeType == 1) {
      if (s99 = s99.childNodes[t5 + (n22 < 0 ? -1 : 0)], s99.nodeType == 1 && s99.contentEditable == "false") return false;
      t5 = n22 < 0 ? Xt(s99) : 0;
    } else return false;
  }
}
function Xt(s99) {
  return s99.nodeType == 3 ? s99.nodeValue.length : s99.childNodes.length;
}
var ds = {
  left: 0,
  right: 0,
  top: 0,
  bottom: 0
};
function ge2(s99, t5) {
  let e4 = t5 ? s99.left : s99.right;
  return {
    left: e4,
    right: e4,
    top: s99.top,
    bottom: s99.bottom
  };
}
function bn(s99) {
  return {
    left: 0,
    right: s99.innerWidth,
    top: 0,
    bottom: s99.innerHeight
  };
}
function yn(s99, t5, e4, i9, n22, r2, o4, l11) {
  let h3 = s99.ownerDocument, a2 = h3.defaultView;
  for (let c4 = s99; c4; ) if (c4.nodeType == 1) {
    let f2, u5 = c4 == h3.body;
    if (u5) f2 = bn(a2);
    else {
      if (c4.scrollHeight <= c4.clientHeight && c4.scrollWidth <= c4.clientWidth) {
        c4 = c4.parentNode;
        continue;
      }
      let m9 = c4.getBoundingClientRect();
      f2 = {
        left: m9.left,
        right: m9.left + c4.clientWidth,
        top: m9.top,
        bottom: m9.top + c4.clientHeight
      };
    }
    let d5 = 0, p5 = 0;
    if (n22 == "nearest") t5.top < f2.top ? (p5 = -(f2.top - t5.top + o4), e4 > 0 && t5.bottom > f2.bottom + p5 && (p5 = t5.bottom - f2.bottom + p5 + o4)) : t5.bottom > f2.bottom && (p5 = t5.bottom - f2.bottom + o4, e4 < 0 && t5.top - p5 < f2.top && (p5 = -(f2.top + p5 - t5.top + o4)));
    else {
      let m9 = t5.bottom - t5.top, b9 = f2.bottom - f2.top;
      p5 = (n22 == "center" && m9 <= b9 ? t5.top + m9 / 2 - b9 / 2 : n22 == "start" || n22 == "center" && e4 < 0 ? t5.top - o4 : t5.bottom - b9 + o4) - f2.top;
    }
    if (i9 == "nearest" ? t5.left < f2.left ? (d5 = -(f2.left - t5.left + r2), e4 > 0 && t5.right > f2.right + d5 && (d5 = t5.right - f2.right + d5 + r2)) : t5.right > f2.right && (d5 = t5.right - f2.right + r2, e4 < 0 && t5.left < f2.left + d5 && (d5 = -(f2.left + d5 - t5.left + r2))) : d5 = (i9 == "center" ? t5.left + (t5.right - t5.left) / 2 - (f2.right - f2.left) / 2 : i9 == "start" == l11 ? t5.left - r2 : t5.right - (f2.right - f2.left) + r2) - f2.left, d5 || p5) if (u5) a2.scrollBy(d5, p5);
    else {
      if (p5) {
        let m9 = c4.scrollTop;
        c4.scrollTop += p5, p5 = c4.scrollTop - m9;
      }
      if (d5) {
        let m9 = c4.scrollLeft;
        c4.scrollLeft += d5, d5 = c4.scrollLeft - m9;
      }
      t5 = {
        left: t5.left - d5,
        top: t5.top - p5,
        right: t5.right - d5,
        bottom: t5.bottom - p5
      };
    }
    if (u5) break;
    c4 = c4.assignedSlot || c4.parentNode, i9 = n22 = "nearest";
  } else if (c4.nodeType == 11) c4 = c4.host;
  else break;
}
var Oe2 = class {
  constructor() {
    this.anchorNode = null, this.anchorOffset = 0, this.focusNode = null, this.focusOffset = 0;
  }
  eq(t5) {
    return this.anchorNode == t5.anchorNode && this.anchorOffset == t5.anchorOffset && this.focusNode == t5.focusNode && this.focusOffset == t5.focusOffset;
  }
  setRange(t5) {
    this.set(t5.anchorNode, t5.anchorOffset, t5.focusNode, t5.focusOffset);
  }
  set(t5, e4, i9, n22) {
    this.anchorNode = t5, this.anchorOffset = e4, this.focusNode = i9, this.focusOffset = n22;
  }
};
var ht2 = null;
function us(s99) {
  if (s99.setActive) return s99.setActive();
  if (ht2) return s99.focus(ht2);
  let t5 = [];
  for (let e4 = s99; e4 && (t5.push(e4, e4.scrollTop, e4.scrollLeft), e4 != e4.ownerDocument); e4 = e4.parentNode) ;
  if (s99.focus(ht2 == null ? {
    get preventScroll() {
      return ht2 = {
        preventScroll: true
      }, true;
    }
  } : void 0), !ht2) {
    ht2 = false;
    for (let e4 = 0; e4 < t5.length; ) {
      let i9 = t5[e4++], n22 = t5[e4++], r2 = t5[e4++];
      i9.scrollTop != n22 && (i9.scrollTop = n22), i9.scrollLeft != r2 && (i9.scrollLeft = r2);
    }
  }
}
var Si;
function Ot(s99, t5, e4 = t5) {
  let i9 = Si || (Si = document.createRange());
  return i9.setEnd(s99, e4), i9.setStart(s99, t5), i9;
}
function Ct(s99, t5, e4) {
  let i9 = {
    key: t5,
    code: t5,
    keyCode: e4,
    which: e4,
    cancelable: true
  }, n22 = new KeyboardEvent("keydown", i9);
  n22.synthetic = true, s99.dispatchEvent(n22);
  let r2 = new KeyboardEvent("keyup", i9);
  return r2.synthetic = true, s99.dispatchEvent(r2), n22.defaultPrevented || r2.defaultPrevented;
}
function wn(s99) {
  for (; s99; ) {
    if (s99 && (s99.nodeType == 9 || s99.nodeType == 11 && s99.host)) return s99;
    s99 = s99.assignedSlot || s99.parentNode;
  }
  return null;
}
function ps(s99) {
  for (; s99.attributes.length; ) s99.removeAttributeNode(s99.attributes[0]);
}
var B2 = class s20 {
  constructor(t5, e4, i9 = true) {
    this.node = t5, this.offset = e4, this.precise = i9;
  }
  static before(t5, e4) {
    return new s20(t5.parentNode, Te2(t5), e4);
  }
  static after(t5, e4) {
    return new s20(t5.parentNode, Te2(t5) + 1, e4);
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
  posBefore(t5) {
    let e4 = this.posAtStart;
    for (let i9 of this.children) {
      if (i9 == t5) return e4;
      e4 += i9.length + i9.breakAfter;
    }
    throw new RangeError("Invalid child in posBefore");
  }
  posAfter(t5) {
    return this.posBefore(t5) + t5.length;
  }
  coordsAt(t5, e4) {
    return null;
  }
  sync(t5) {
    if (this.dirty & 2) {
      let e4 = this.dom, i9 = null, n22;
      for (let r2 of this.children) {
        if (r2.dirty) {
          if (!r2.dom && (n22 = i9 ? i9.nextSibling : e4.firstChild)) {
            let o4 = s21.get(n22);
            (!o4 || !o4.parent && o4.constructor == r2.constructor) && r2.reuseDOM(n22);
          }
          r2.sync(t5), r2.dirty = 0;
        }
        if (n22 = i9 ? i9.nextSibling : e4.firstChild, t5 && !t5.written && t5.node == e4 && n22 != r2.dom && (t5.written = true), r2.dom.parentNode == e4) for (; n22 && n22 != r2.dom; ) n22 = Ci(n22);
        else e4.insertBefore(r2.dom, n22);
        i9 = r2.dom;
      }
      for (n22 = i9 ? i9.nextSibling : e4.firstChild, n22 && t5 && t5.node == e4 && (t5.written = true); n22; ) n22 = Ci(n22);
    } else if (this.dirty & 1) for (let e4 of this.children) e4.dirty && (e4.sync(t5), e4.dirty = 0);
  }
  reuseDOM(t5) {
  }
  localPosFromDOM(t5, e4) {
    let i9;
    if (t5 == this.dom) i9 = this.dom.childNodes[e4];
    else {
      let n22 = Xt(t5) == 0 ? 0 : e4 == 0 ? -1 : 1;
      for (; ; ) {
        let r2 = t5.parentNode;
        if (r2 == this.dom) break;
        n22 == 0 && r2.firstChild != r2.lastChild && (t5 == r2.firstChild ? n22 = -1 : n22 = 1), t5 = r2;
      }
      n22 < 0 ? i9 = t5 : i9 = t5.nextSibling;
    }
    if (i9 == this.dom.firstChild) return 0;
    for (; i9 && !s21.get(i9); ) i9 = i9.nextSibling;
    if (!i9) return this.length;
    for (let n22 = 0, r2 = 0; ; n22++) {
      let o4 = this.children[n22];
      if (o4.dom == i9) return r2;
      r2 += o4.length + o4.breakAfter;
    }
  }
  domBoundsAround(t5, e4, i9 = 0) {
    let n22 = -1, r2 = -1, o4 = -1, l11 = -1;
    for (let h3 = 0, a2 = i9, c4 = i9; h3 < this.children.length; h3++) {
      let f2 = this.children[h3], u5 = a2 + f2.length;
      if (a2 < t5 && u5 > e4) return f2.domBoundsAround(t5, e4, a2);
      if (u5 >= t5 && n22 == -1 && (n22 = h3, r2 = a2), a2 > e4 && f2.dom.parentNode == this.dom) {
        o4 = h3, l11 = c4;
        break;
      }
      c4 = u5, a2 = u5 + f2.breakAfter;
    }
    return {
      from: r2,
      to: l11 < 0 ? i9 + this.length : l11,
      startDOM: (n22 ? this.children[n22 - 1].dom.nextSibling : null) || this.dom.firstChild,
      endDOM: o4 < this.children.length && o4 >= 0 ? this.children[o4].dom : null
    };
  }
  markDirty(t5 = false) {
    this.dirty |= 2, this.markParentsDirty(t5);
  }
  markParentsDirty(t5) {
    for (let e4 = this.parent; e4; e4 = e4.parent) {
      if (t5 && (e4.dirty |= 2), e4.dirty & 1) return;
      e4.dirty |= 1, t5 = false;
    }
  }
  setParent(t5) {
    this.parent != t5 && (this.parent = t5, this.dirty && this.markParentsDirty(true));
  }
  setDOM(t5) {
    this.dom && (this.dom.cmView = null), this.dom = t5, t5.cmView = this;
  }
  get rootView() {
    for (let t5 = this; ; ) {
      let e4 = t5.parent;
      if (!e4) return t5;
      t5 = e4;
    }
  }
  replaceChildren(t5, e4, i9 = mi) {
    this.markDirty();
    for (let n22 = t5; n22 < e4; n22++) {
      let r2 = this.children[n22];
      r2.parent == this && r2.destroy();
    }
    this.children.splice(t5, e4 - t5, ...i9);
    for (let n22 = 0; n22 < i9.length; n22++) i9[n22].setParent(this);
  }
  ignoreMutation(t5) {
    return false;
  }
  ignoreEvent(t5) {
    return false;
  }
  childCursor(t5 = this.length) {
    return new Jt(this.children, t5, this.children.length);
  }
  childPos(t5, e4 = 1) {
    return this.childCursor().findPos(t5, e4);
  }
  toString() {
    let t5 = this.constructor.name.replace("View", "");
    return t5 + (this.children.length ? "(" + this.children.join() + ")" : this.length ? "[" + (t5 == "Text" ? this.text : this.length) + "]" : "") + (this.breakAfter ? "#" : "");
  }
  static get(t5) {
    return t5.cmView;
  }
  get isEditable() {
    return true;
  }
  merge(t5, e4, i9, n22, r2, o4) {
    return false;
  }
  become(t5) {
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
function Ci(s99) {
  let t5 = s99.nextSibling;
  return s99.parentNode.removeChild(s99), t5;
}
var Jt = class {
  constructor(t5, e4, i9) {
    this.children = t5, this.pos = e4, this.i = i9, this.off = 0;
  }
  findPos(t5, e4 = 1) {
    for (; ; ) {
      if (t5 > this.pos || t5 == this.pos && (e4 > 0 || this.i == 0 || this.children[this.i - 1].breakAfter)) return this.off = t5 - this.pos, this;
      let i9 = this.children[--this.i];
      this.pos -= i9.length + i9.breakAfter;
    }
  }
};
function ms(s99, t5, e4, i9, n22, r2, o4, l11, h3) {
  let { children: a2 } = s99, c4 = a2.length ? a2[t5] : null, f2 = r2.length ? r2[r2.length - 1] : null, u5 = f2 ? f2.breakAfter : o4;
  if (!(t5 == i9 && c4 && !o4 && !u5 && r2.length < 2 && c4.merge(e4, n22, r2.length ? f2 : null, e4 == 0, l11, h3))) {
    if (i9 < a2.length) {
      let d5 = a2[i9];
      d5 && n22 < d5.length ? (t5 == i9 && (d5 = d5.split(n22), n22 = 0), !u5 && f2 && d5.merge(0, n22, f2, true, 0, h3) ? r2[r2.length - 1] = d5 : (n22 && d5.merge(0, n22, null, false, 0, h3), r2.push(d5))) : d5?.breakAfter && (f2 ? f2.breakAfter = 1 : o4 = 1), i9++;
    }
    for (c4 && (c4.breakAfter = o4, e4 > 0 && (!o4 && r2.length && c4.merge(e4, c4.length, r2[0], false, l11, 0) ? c4.breakAfter = r2.shift().breakAfter : (e4 < c4.length || c4.children.length && c4.children[c4.children.length - 1].length == 0) && c4.merge(e4, c4.length, null, false, l11, 0), t5++)); t5 < i9 && r2.length; ) if (a2[i9 - 1].become(r2[r2.length - 1])) i9--, r2.pop(), h3 = r2.length ? 0 : l11;
    else if (a2[t5].become(r2[0])) t5++, r2.shift(), l11 = r2.length ? 0 : h3;
    else break;
    !r2.length && t5 && i9 < a2.length && !a2[t5 - 1].breakAfter && a2[i9].merge(0, 0, a2[t5 - 1], false, l11, h3) && t5--, (t5 < i9 || r2.length) && s99.replaceChildren(t5, i9, r2);
  }
}
function gs(s99, t5, e4, i9, n22, r2) {
  let o4 = s99.childCursor(), { i: l11, off: h3 } = o4.findPos(e4, 1), { i: a2, off: c4 } = o4.findPos(t5, -1), f2 = t5 - e4;
  for (let u5 of i9) f2 += u5.length;
  s99.length += f2, ms(s99, a2, c4, l11, h3, i9, 0, n22, r2);
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
  constructor(t5) {
    super(), this.text = t5;
  }
  get length() {
    return this.text.length;
  }
  createDOM(t5) {
    this.setDOM(t5 || document.createTextNode(this.text));
  }
  sync(t5) {
    this.dom || this.createDOM(), this.dom.nodeValue != this.text && (t5 && t5.node == this.dom && (t5.written = true), this.dom.nodeValue = this.text);
  }
  reuseDOM(t5) {
    t5.nodeType == 3 && this.createDOM(t5);
  }
  merge(t5, e4, i9) {
    return i9 && (!(i9 instanceof s22) || this.length - (e4 - t5) + i9.length > vn) ? false : (this.text = this.text.slice(0, t5) + (i9 ? i9.text : "") + this.text.slice(e4), this.markDirty(), true);
  }
  split(t5) {
    let e4 = new s22(this.text.slice(t5));
    return this.text = this.text.slice(0, t5), this.markDirty(), e4;
  }
  localPosFromDOM(t5, e4) {
    return t5 == this.dom ? e4 : e4 ? this.text.length : 0;
  }
  domAtPos(t5) {
    return new B2(this.dom, t5);
  }
  domBoundsAround(t5, e4, i9) {
    return {
      from: i9,
      to: i9 + this.length,
      startDOM: this.dom,
      endDOM: this.dom.nextSibling
    };
  }
  coordsAt(t5, e4) {
    return Be2(this.dom, t5, e4);
  }
};
var q2 = class s23 extends R2 {
  constructor(t5, e4 = [], i9 = 0) {
    super(), this.mark = t5, this.children = e4, this.length = i9;
    for (let n22 of e4) n22.setParent(this);
  }
  setAttrs(t5) {
    if (ps(t5), this.mark.class && (t5.className = this.mark.class), this.mark.attrs) for (let e4 in this.mark.attrs) t5.setAttribute(e4, this.mark.attrs[e4]);
    return t5;
  }
  reuseDOM(t5) {
    t5.nodeName == this.mark.tagName.toUpperCase() && (this.setDOM(t5), this.dirty |= 6);
  }
  sync(t5) {
    this.dom ? this.dirty & 4 && this.setAttrs(this.dom) : this.setDOM(this.setAttrs(document.createElement(this.mark.tagName))), super.sync(t5);
  }
  merge(t5, e4, i9, n22, r2, o4) {
    return i9 && (!(i9 instanceof s23 && i9.mark.eq(this.mark)) || t5 && r2 <= 0 || e4 < this.length && o4 <= 0) ? false : (gs(this, t5, e4, i9 ? i9.children : [], r2 - 1, o4 - 1), this.markDirty(), true);
  }
  split(t5) {
    let e4 = [], i9 = 0, n22 = -1, r2 = 0;
    for (let l11 of this.children) {
      let h3 = i9 + l11.length;
      h3 > t5 && e4.push(i9 < t5 ? l11.split(t5 - i9) : l11), n22 < 0 && i9 >= t5 && (n22 = r2), i9 = h3, r2++;
    }
    let o4 = this.length - t5;
    return this.length = t5, n22 > -1 && (this.children.length = n22, this.markDirty()), new s23(this.mark, e4, o4);
  }
  domAtPos(t5) {
    return vs(this.dom, this.children, t5);
  }
  coordsAt(t5, e4) {
    return Ss(this, t5, e4);
  }
};
function Be2(s99, t5, e4) {
  let i9 = s99.nodeValue.length;
  t5 > i9 && (t5 = i9);
  let n22 = t5, r2 = t5, o4 = 0;
  t5 == 0 && e4 < 0 || t5 == i9 && e4 >= 0 ? g2.chrome || g2.gecko || (t5 ? (n22--, o4 = 1) : r2 < i9 && (r2++, o4 = -1)) : e4 < 0 ? n22-- : r2 < i9 && r2++;
  let l11 = Ot(s99, n22, r2).getClientRects();
  if (!l11.length) return ds;
  let h3 = l11[(o4 ? o4 < 0 : e4 >= 0) ? 0 : l11.length - 1];
  return g2.safari && !o4 && h3.width == 0 && (h3 = Array.prototype.find.call(l11, (a2) => a2.width) || h3), o4 ? ge2(h3, o4 < 0) : h3 || null;
}
var Rt = class s24 extends R2 {
  constructor(t5, e4, i9) {
    super(), this.widget = t5, this.length = e4, this.side = i9, this.prevWidget = null;
  }
  static create(t5, e4, i9) {
    return new (t5.customView || s24)(t5, e4, i9);
  }
  split(t5) {
    let e4 = s24.create(this.widget, this.length - t5, this.side);
    return this.length -= t5, e4;
  }
  sync() {
    (!this.dom || !this.widget.updateDOM(this.dom)) && (this.dom && this.prevWidget && this.prevWidget.destroy(this.dom), this.prevWidget = null, this.setDOM(this.widget.toDOM(this.editorView)), this.dom.contentEditable = "false");
  }
  getSide() {
    return this.side;
  }
  merge(t5, e4, i9, n22, r2, o4) {
    return i9 && (!(i9 instanceof s24) || !this.widget.compare(i9.widget) || t5 > 0 && r2 <= 0 || e4 < this.length && o4 <= 0) ? false : (this.length = t5 + (i9 ? i9.length : 0) + (this.length - e4), true);
  }
  become(t5) {
    return t5.length == this.length && t5 instanceof s24 && t5.side == this.side && this.widget.constructor == t5.widget.constructor ? (this.widget.eq(t5.widget) || this.markDirty(true), this.dom && !this.prevWidget && (this.prevWidget = this.widget), this.widget = t5.widget, true) : false;
  }
  ignoreMutation() {
    return true;
  }
  ignoreEvent(t5) {
    return this.widget.ignoreEvent(t5);
  }
  get overrideDOMText() {
    if (this.length == 0) return m.empty;
    let t5 = this;
    for (; t5.parent; ) t5 = t5.parent;
    let e4 = t5.editorView, i9 = e4 && e4.state.doc, n22 = this.posAtStart;
    return i9 ? i9.slice(n22, n22 + this.length) : m.empty;
  }
  domAtPos(t5) {
    return t5 == 0 ? B2.before(this.dom) : B2.after(this.dom, t5 == this.length);
  }
  domBoundsAround() {
    return null;
  }
  coordsAt(t5, e4) {
    let i9 = this.dom.getClientRects(), n22 = null;
    if (!i9.length) return ds;
    for (let r2 = t5 > 0 ? i9.length - 1 : 0; n22 = i9[r2], !(t5 > 0 ? r2 == 0 : r2 == i9.length - 1 || n22.top < n22.bottom); r2 += t5 > 0 ? -1 : 1) ;
    return t5 == 0 && e4 > 0 || t5 == this.length && e4 <= 0 ? n22 : ge2(n22, t5 == 0);
  }
  get isEditable() {
    return false;
  }
  destroy() {
    super.destroy(), this.dom && this.widget.destroy(this.dom);
  }
};
var Zt = class extends Rt {
  domAtPos(t5) {
    let { topView: e4, text: i9 } = this.widget;
    return e4 ? He2(t5, 0, e4, i9, (n22, r2) => n22.domAtPos(r2), (n22) => new B2(i9, Math.min(n22, i9.nodeValue.length))) : new B2(i9, Math.min(t5, i9.nodeValue.length));
  }
  sync() {
    this.setDOM(this.widget.toDOM());
  }
  localPosFromDOM(t5, e4) {
    let { topView: i9, text: n22 } = this.widget;
    return i9 ? ws(t5, e4, i9, n22) : Math.min(e4, this.length);
  }
  ignoreMutation() {
    return false;
  }
  get overrideDOMText() {
    return null;
  }
  coordsAt(t5, e4) {
    let { topView: i9, text: n22 } = this.widget;
    return i9 ? He2(t5, e4, i9, n22, (r2, o4, l11) => r2.coordsAt(o4, l11), (r2, o4) => Be2(n22, r2, o4)) : Be2(n22, t5, e4);
  }
  destroy() {
    var t5;
    super.destroy(), (t5 = this.widget.topView) === null || t5 === void 0 || t5.destroy();
  }
  get isEditable() {
    return true;
  }
};
function He2(s99, t5, e4, i9, n22, r2) {
  if (e4 instanceof q2) {
    for (let o4 of e4.children) {
      let l11 = pt(o4.dom, i9), h3 = l11 ? i9.nodeValue.length : o4.length;
      if (s99 < h3 || s99 == h3 && o4.getSide() <= 0) return l11 ? He2(s99, t5, o4, i9, n22, r2) : n22(o4, s99, t5);
      s99 -= h3;
    }
    return n22(e4, e4.length, -1);
  } else return e4.dom == i9 ? r2(s99, t5) : n22(e4, s99, t5);
}
function ws(s99, t5, e4, i9) {
  if (e4 instanceof q2) for (let n22 of e4.children) {
    let r2 = 0, o4 = pt(n22.dom, i9);
    if (pt(n22.dom, s99)) return r2 + (o4 ? ws(s99, t5, n22, i9) : n22.localPosFromDOM(s99, t5));
    r2 += o4 ? i9.nodeValue.length : n22.length;
  }
  else if (e4.dom == i9) return Math.min(t5, i9.nodeValue.length);
  return e4.localPosFromDOM(s99, t5);
}
var Lt = class s25 extends R2 {
  constructor(t5) {
    super(), this.side = t5;
  }
  get length() {
    return 0;
  }
  merge() {
    return false;
  }
  become(t5) {
    return t5 instanceof s25 && t5.side == this.side;
  }
  split() {
    return new s25(this.side);
  }
  sync() {
    if (!this.dom) {
      let t5 = document.createElement("img");
      t5.className = "cm-widgetBuffer", t5.setAttribute("aria-hidden", "true"), this.setDOM(t5);
    }
  }
  getSide() {
    return this.side;
  }
  domAtPos(t5) {
    return B2.before(this.dom);
  }
  localPosFromDOM() {
    return 0;
  }
  domBoundsAround() {
    return null;
  }
  coordsAt(t5) {
    let e4 = this.dom.getBoundingClientRect(), i9 = xn(this, this.side > 0 ? -1 : 1);
    return i9 && i9.top < e4.bottom && i9.bottom > e4.top ? {
      left: e4.left,
      right: e4.right,
      top: i9.top,
      bottom: i9.bottom
    } : e4;
  }
  get overrideDOMText() {
    return m.empty;
  }
};
rt2.prototype.children = Rt.prototype.children = Lt.prototype.children = mi;
function xn(s99, t5) {
  let e4 = s99.parent, i9 = e4 ? e4.children.indexOf(s99) : -1;
  for (; e4 && i9 >= 0; ) if (t5 < 0 ? i9 > 0 : i9 < e4.children.length) {
    let n22 = e4.children[i9 + t5];
    if (n22 instanceof rt2) {
      let r2 = n22.coordsAt(t5 < 0 ? n22.length : 0, t5);
      if (r2) return r2;
    }
    i9 += t5;
  } else if (e4 instanceof q2 && e4.parent) i9 = e4.parent.children.indexOf(e4) + (t5 < 0 ? 0 : 1), e4 = e4.parent;
  else {
    let n22 = e4.dom.lastChild;
    if (n22 && n22.nodeName == "BR") return n22.getClientRects()[0];
    break;
  }
}
function vs(s99, t5, e4) {
  let i9 = 0;
  for (let n22 = 0; i9 < t5.length; i9++) {
    let r2 = t5[i9], o4 = n22 + r2.length;
    if (!(o4 == n22 && r2.getSide() <= 0)) {
      if (e4 > n22 && e4 < o4 && r2.dom.parentNode == s99) return r2.domAtPos(e4 - n22);
      if (e4 <= n22) break;
      n22 = o4;
    }
  }
  for (; i9 > 0; i9--) {
    let n22 = t5[i9 - 1].dom;
    if (n22.parentNode == s99) return B2.after(n22);
  }
  return new B2(s99, 0);
}
function xs(s99, t5, e4) {
  let i9, { children: n22 } = s99;
  e4 > 0 && t5 instanceof q2 && n22.length && (i9 = n22[n22.length - 1]) instanceof q2 && i9.mark.eq(t5.mark) ? xs(i9, t5.children[0], e4 - 1) : (n22.push(t5), t5.setParent(s99)), s99.length += t5.length;
}
function Ss(s99, t5, e4) {
  for (let r2 = 0, o4 = 0; o4 < s99.children.length; o4++) {
    let l11 = s99.children[o4], h3 = r2 + l11.length, a2;
    if ((e4 <= 0 || h3 == s99.length || l11.getSide() > 0 ? h3 >= t5 : h3 > t5) && (t5 < h3 || o4 + 1 == s99.children.length || (a2 = s99.children[o4 + 1]).length || a2.getSide() > 0)) {
      let c4 = 0;
      if (h3 == r2) {
        if (l11.getSide() <= 0) continue;
        c4 = e4 = -l11.getSide();
      }
      let f2 = l11.coordsAt(Math.max(0, t5 - r2), e4);
      return c4 && f2 ? ge2(f2, e4 < 0) : f2;
    }
    r2 = h3;
  }
  let i9 = s99.dom.lastChild;
  if (!i9) return s99.dom.getBoundingClientRect();
  let n22 = Tt(i9);
  return n22[n22.length - 1] || null;
}
function Pe2(s99, t5) {
  for (let e4 in s99) e4 == "class" && t5.class ? t5.class += " " + s99.class : e4 == "style" && t5.style ? t5.style += ";" + s99.style : t5[e4] = s99[e4];
  return t5;
}
function gi(s99, t5) {
  if (s99 == t5) return true;
  if (!s99 || !t5) return false;
  let e4 = Object.keys(s99), i9 = Object.keys(t5);
  if (e4.length != i9.length) return false;
  for (let n22 of e4) if (i9.indexOf(n22) == -1 || s99[n22] !== t5[n22]) return false;
  return true;
}
function Ve2(s99, t5, e4) {
  let i9 = null;
  if (t5) for (let n22 in t5) e4 && n22 in e4 || s99.removeAttribute(i9 = n22);
  if (e4) for (let n22 in e4) t5 && t5[n22] == e4[n22] || s99.setAttribute(i9 = n22, e4[n22]);
  return !!i9;
}
var K2 = class {
  eq(t5) {
    return false;
  }
  updateDOM(t5) {
    return false;
  }
  compare(t5) {
    return this == t5 || this.constructor == t5.constructor && this.eq(t5);
  }
  get estimatedHeight() {
    return -1;
  }
  ignoreEvent(t5) {
    return true;
  }
  get customView() {
    return null;
  }
  destroy(t5) {
  }
};
var D2 = function(s99) {
  return s99[s99.Text = 0] = "Text", s99[s99.WidgetBefore = 1] = "WidgetBefore", s99[s99.WidgetAfter = 2] = "WidgetAfter", s99[s99.WidgetRange = 3] = "WidgetRange", s99;
}(D2 || (D2 = {}));
var C2 = class extends z {
  constructor(t5, e4, i9, n22) {
    super(), this.startSide = t5, this.endSide = e4, this.widget = i9, this.spec = n22;
  }
  get heightRelevant() {
    return false;
  }
  static mark(t5) {
    return new Qt(t5);
  }
  static widget(t5) {
    let e4 = t5.side || 0, i9 = !!t5.block;
    return e4 += i9 ? e4 > 0 ? 3e8 : -4e8 : e4 > 0 ? 1e8 : -1e8, new ot2(t5, e4, e4, i9, t5.widget || null, false);
  }
  static replace(t5) {
    let e4 = !!t5.block, i9, n22;
    if (t5.isBlockGap) i9 = -5e8, n22 = 4e8;
    else {
      let { start: r2, end: o4 } = Cs(t5, e4);
      i9 = (r2 ? e4 ? -3e8 : -1 : 5e8) - 1, n22 = (o4 ? e4 ? 2e8 : 1 : -6e8) + 1;
    }
    return new ot2(t5, i9, n22, e4, t5.widget || null, true);
  }
  static line(t5) {
    return new Et(t5);
  }
  static set(t5, e4 = false) {
    return O.of(t5, e4);
  }
  hasHeight() {
    return this.widget ? this.widget.estimatedHeight > -1 : false;
  }
};
C2.none = O.empty;
var Qt = class s26 extends C2 {
  constructor(t5) {
    let { start: e4, end: i9 } = Cs(t5);
    super(e4 ? -1 : 5e8, i9 ? 1 : -6e8, null, t5), this.tagName = t5.tagName || "span", this.class = t5.class || "", this.attrs = t5.attributes || null;
  }
  eq(t5) {
    return this == t5 || t5 instanceof s26 && this.tagName == t5.tagName && this.class == t5.class && gi(this.attrs, t5.attrs);
  }
  range(t5, e4 = t5) {
    if (t5 >= e4) throw new RangeError("Mark decorations may not be empty");
    return super.range(t5, e4);
  }
};
Qt.prototype.point = false;
var Et = class s27 extends C2 {
  constructor(t5) {
    super(-2e8, -2e8, null, t5);
  }
  eq(t5) {
    return t5 instanceof s27 && gi(this.spec.attributes, t5.spec.attributes);
  }
  range(t5, e4 = t5) {
    if (e4 != t5) throw new RangeError("Line decoration ranges must be zero-length");
    return super.range(t5, e4);
  }
};
Et.prototype.mapMode = b.TrackBefore;
Et.prototype.point = true;
var ot2 = class s28 extends C2 {
  constructor(t5, e4, i9, n22, r2, o4) {
    super(e4, i9, r2, t5), this.block = n22, this.isReplace = o4, this.mapMode = n22 ? e4 <= 0 ? b.TrackBefore : b.TrackAfter : b.TrackDel;
  }
  get type() {
    return this.startSide < this.endSide ? D2.WidgetRange : this.startSide <= 0 ? D2.WidgetBefore : D2.WidgetAfter;
  }
  get heightRelevant() {
    return this.block || !!this.widget && this.widget.estimatedHeight >= 5;
  }
  eq(t5) {
    return t5 instanceof s28 && Sn(this.widget, t5.widget) && this.block == t5.block && this.startSide == t5.startSide && this.endSide == t5.endSide;
  }
  range(t5, e4 = t5) {
    if (this.isReplace && (t5 > e4 || t5 == e4 && this.startSide > 0 && this.endSide <= 0)) throw new RangeError("Invalid range for replacement decoration");
    if (!this.isReplace && e4 != t5) throw new RangeError("Widget decorations can only have zero-length ranges");
    return super.range(t5, e4);
  }
};
ot2.prototype.point = true;
function Cs(s99, t5 = false) {
  let { inclusiveStart: e4, inclusiveEnd: i9 } = s99;
  return e4 == null && (e4 = s99.inclusive), i9 == null && (i9 = s99.inclusive), {
    start: e4 ?? t5,
    end: i9 ?? t5
  };
}
function Sn(s99, t5) {
  return s99 == t5 || !!(s99 && t5 && s99.compare(t5));
}
function Ne2(s99, t5, e4, i9 = 0) {
  let n22 = e4.length - 1;
  n22 >= 0 && e4[n22] + i9 >= s99 ? e4[n22] = Math.max(e4[n22], t5) : e4.push(s99, t5);
}
var N2 = class s29 extends R2 {
  constructor() {
    super(...arguments), this.children = [], this.length = 0, this.prevAttrs = void 0, this.attrs = null, this.breakAfter = 0;
  }
  merge(t5, e4, i9, n22, r2, o4) {
    if (i9) {
      if (!(i9 instanceof s29)) return false;
      this.dom || i9.transferDOM(this);
    }
    return n22 && this.setDeco(i9 ? i9.attrs : null), gs(this, t5, e4, i9 ? i9.children : [], r2, o4), true;
  }
  split(t5) {
    let e4 = new s29();
    if (e4.breakAfter = this.breakAfter, this.length == 0) return e4;
    let { i: i9, off: n22 } = this.childPos(t5);
    n22 && (e4.append(this.children[i9].split(n22), 0), this.children[i9].merge(n22, this.children[i9].length, null, false, 0, 0), i9++);
    for (let r2 = i9; r2 < this.children.length; r2++) e4.append(this.children[r2], 0);
    for (; i9 > 0 && this.children[i9 - 1].length == 0; ) this.children[--i9].destroy();
    return this.children.length = i9, this.markDirty(), this.length = t5, e4;
  }
  transferDOM(t5) {
    this.dom && (this.markDirty(), t5.setDOM(this.dom), t5.prevAttrs = this.prevAttrs === void 0 ? this.attrs : this.prevAttrs, this.prevAttrs = void 0, this.dom = null);
  }
  setDeco(t5) {
    gi(this.attrs, t5) || (this.dom && (this.prevAttrs = this.attrs, this.markDirty()), this.attrs = t5);
  }
  append(t5, e4) {
    xs(this, t5, e4);
  }
  addLineDeco(t5) {
    let e4 = t5.spec.attributes, i9 = t5.spec.class;
    e4 && (this.attrs = Pe2(e4, this.attrs || {})), i9 && (this.attrs = Pe2({
      class: i9
    }, this.attrs || {}));
  }
  domAtPos(t5) {
    return vs(this.dom, this.children, t5);
  }
  reuseDOM(t5) {
    t5.nodeName == "DIV" && (this.setDOM(t5), this.dirty |= 6);
  }
  sync(t5) {
    var e4;
    this.dom ? this.dirty & 4 && (ps(this.dom), this.dom.className = "cm-line", this.prevAttrs = this.attrs ? null : void 0) : (this.setDOM(document.createElement("div")), this.dom.className = "cm-line", this.prevAttrs = this.attrs ? null : void 0), this.prevAttrs !== void 0 && (Ve2(this.dom, this.prevAttrs, this.attrs), this.dom.classList.add("cm-line"), this.prevAttrs = void 0), super.sync(t5);
    let i9 = this.dom.lastChild;
    for (; i9 && R2.get(i9) instanceof q2; ) i9 = i9.lastChild;
    if (!i9 || !this.length || i9.nodeName != "BR" && ((e4 = R2.get(i9)) === null || e4 === void 0 ? void 0 : e4.isEditable) == false && (!g2.ios || !this.children.some((n22) => n22 instanceof rt2))) {
      let n22 = document.createElement("BR");
      n22.cmIgnore = true, this.dom.appendChild(n22);
    }
  }
  measureTextSize() {
    if (this.children.length == 0 || this.length > 20) return null;
    let t5 = 0;
    for (let e4 of this.children) {
      if (!(e4 instanceof rt2)) return null;
      let i9 = Tt(e4.dom);
      if (i9.length != 1) return null;
      t5 += i9[0].width;
    }
    return {
      lineHeight: this.dom.getBoundingClientRect().height,
      charWidth: t5 / this.length
    };
  }
  coordsAt(t5, e4) {
    return Ss(this, t5, e4);
  }
  become(t5) {
    return false;
  }
  get type() {
    return D2.Text;
  }
  static find(t5, e4) {
    for (let i9 = 0, n22 = 0; i9 < t5.children.length; i9++) {
      let r2 = t5.children[i9], o4 = n22 + r2.length;
      if (o4 >= e4) {
        if (r2 instanceof s29) return r2;
        if (o4 > e4) break;
      }
      n22 = o4 + r2.breakAfter;
    }
    return null;
  }
};
var Bt = class s30 extends R2 {
  constructor(t5, e4, i9) {
    super(), this.widget = t5, this.length = e4, this.type = i9, this.breakAfter = 0, this.prevWidget = null;
  }
  merge(t5, e4, i9, n22, r2, o4) {
    return i9 && (!(i9 instanceof s30) || !this.widget.compare(i9.widget) || t5 > 0 && r2 <= 0 || e4 < this.length && o4 <= 0) ? false : (this.length = t5 + (i9 ? i9.length : 0) + (this.length - e4), true);
  }
  domAtPos(t5) {
    return t5 == 0 ? B2.before(this.dom) : B2.after(this.dom, t5 == this.length);
  }
  split(t5) {
    let e4 = this.length - t5;
    this.length = t5;
    let i9 = new s30(this.widget, e4, this.type);
    return i9.breakAfter = this.breakAfter, i9;
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
  become(t5) {
    return t5 instanceof s30 && t5.type == this.type && t5.widget.constructor == this.widget.constructor ? (t5.widget.eq(this.widget) || this.markDirty(true), this.dom && !this.prevWidget && (this.prevWidget = this.widget), this.widget = t5.widget, this.length = t5.length, this.breakAfter = t5.breakAfter, true) : false;
  }
  ignoreMutation() {
    return true;
  }
  ignoreEvent(t5) {
    return this.widget.ignoreEvent(t5);
  }
  destroy() {
    super.destroy(), this.dom && this.widget.destroy(this.dom);
  }
};
var We2 = class s31 {
  constructor(t5, e4, i9, n22) {
    this.doc = t5, this.pos = e4, this.end = i9, this.disallowBlockEffectsFor = n22, this.content = [], this.curLine = null, this.breakAtStart = 0, this.pendingBuffer = 0, this.atCursorPos = true, this.openStart = -1, this.openEnd = -1, this.text = "", this.textOff = 0, this.cursor = t5.iter(), this.skip = e4;
  }
  posCovered() {
    if (this.content.length == 0) return !this.breakAtStart && this.doc.lineAt(this.pos).from != this.pos;
    let t5 = this.content[this.content.length - 1];
    return !t5.breakAfter && !(t5 instanceof Bt && t5.type == D2.WidgetBefore);
  }
  getLine() {
    return this.curLine || (this.content.push(this.curLine = new N2()), this.atCursorPos = true), this.curLine;
  }
  flushBuffer(t5) {
    this.pendingBuffer && (this.curLine.append(It(new Lt(-1), t5), t5.length), this.pendingBuffer = 0);
  }
  addBlockWidget(t5) {
    this.flushBuffer([]), this.curLine = null, this.content.push(t5);
  }
  finish(t5) {
    t5 ? this.pendingBuffer = 0 : this.flushBuffer([]), this.posCovered() || this.getLine();
  }
  buildText(t5, e4, i9) {
    for (; t5 > 0; ) {
      if (this.textOff == this.text.length) {
        let { value: r2, lineBreak: o4, done: l11 } = this.cursor.next(this.skip);
        if (this.skip = 0, l11) throw new Error("Ran out of text content when drawing inline views");
        if (o4) {
          this.posCovered() || this.getLine(), this.content.length ? this.content[this.content.length - 1].breakAfter = 1 : this.breakAtStart = 1, this.flushBuffer([]), this.curLine = null, t5--;
          continue;
        } else this.text = r2, this.textOff = 0;
      }
      let n22 = Math.min(this.text.length - this.textOff, t5, 512);
      this.flushBuffer(e4.slice(0, i9)), this.getLine().append(It(new rt2(this.text.slice(this.textOff, this.textOff + n22)), e4), i9), this.atCursorPos = true, this.textOff += n22, t5 -= n22, i9 = 0;
    }
  }
  span(t5, e4, i9, n22) {
    this.buildText(e4 - t5, i9, n22), this.pos = e4, this.openStart < 0 && (this.openStart = n22);
  }
  point(t5, e4, i9, n22, r2, o4) {
    if (this.disallowBlockEffectsFor[o4] && i9 instanceof ot2) {
      if (i9.block) throw new RangeError("Block decorations may not be specified via plugins");
      if (e4 > this.doc.lineAt(this.pos).to) throw new RangeError("Decorations that replace line breaks may not be specified via plugins");
    }
    let l11 = e4 - t5;
    if (i9 instanceof ot2) if (i9.block) {
      let { type: h3 } = i9;
      h3 == D2.WidgetAfter && !this.posCovered() && this.getLine(), this.addBlockWidget(new Bt(i9.widget || new te2("div"), l11, h3));
    } else {
      let h3 = Rt.create(i9.widget || new te2("span"), l11, i9.startSide), a2 = this.atCursorPos && !h3.isEditable && r2 <= n22.length && (t5 < e4 || i9.startSide > 0), c4 = !h3.isEditable && (t5 < e4 || i9.startSide <= 0), f2 = this.getLine();
      this.pendingBuffer == 2 && !a2 && (this.pendingBuffer = 0), this.flushBuffer(n22), a2 && (f2.append(It(new Lt(1), n22), r2), r2 = n22.length + Math.max(0, r2 - n22.length)), f2.append(It(h3, n22), r2), this.atCursorPos = c4, this.pendingBuffer = c4 ? t5 < e4 ? 1 : 2 : 0;
    }
    else this.doc.lineAt(this.pos).from == this.pos && this.getLine().addLineDeco(i9);
    l11 && (this.textOff + l11 <= this.text.length ? this.textOff += l11 : (this.skip += l11 - (this.text.length - this.textOff), this.text = "", this.textOff = 0), this.pos = e4), this.openStart < 0 && (this.openStart = r2);
  }
  static build(t5, e4, i9, n22, r2) {
    let o4 = new s31(t5, e4, i9, r2);
    return o4.openEnd = O.spans(n22, e4, i9, o4), o4.openStart < 0 && (o4.openStart = o4.openEnd), o4.finish(o4.openEnd), o4;
  }
};
function It(s99, t5) {
  for (let e4 of t5) s99 = new q2(e4, [
    s99
  ], s99.length);
  return s99;
}
var te2 = class extends K2 {
  constructor(t5) {
    super(), this.tag = t5;
  }
  eq(t5) {
    return t5.tag == this.tag;
  }
  toDOM() {
    return document.createElement(this.tag);
  }
  updateDOM(t5) {
    return t5.nodeName.toLowerCase() == this.tag;
  }
};
var Ms = y.define();
var ks = y.define();
var As = y.define();
var Ds = y.define();
var ze2 = y.define();
var Ts = y.define();
var Os = y.define({
  combine: (s99) => s99.some((t5) => t5)
});
var ee2 = class s32 {
  constructor(t5, e4 = "nearest", i9 = "nearest", n22 = 5, r2 = 5) {
    this.range = t5, this.y = e4, this.x = i9, this.yMargin = n22, this.xMargin = r2;
  }
  map(t5) {
    return t5.empty ? this : new s32(this.range.map(t5), this.y, this.x, this.yMargin, this.xMargin);
  }
};
var Di = v.define({
  map: (s99, t5) => s99.map(t5)
});
function Z2(s99, t5, e4) {
  let i9 = s99.facet(Ds);
  i9.length ? i9[0](t5) : globalThis.onerror ? globalThis.onerror(String(t5), e4, void 0, void 0, t5) : e4 ? console.error(e4 + ":", t5) : console.error(t5);
}
var Nt = y.define({
  combine: (s99) => s99.length ? s99[0] : true
});
var Cn = 0;
var bt = y.define();
var P2 = class s33 {
  constructor(t5, e4, i9, n22) {
    this.id = t5, this.create = e4, this.domEventHandlers = i9, this.extension = n22(this);
  }
  static define(t5, e4) {
    let { eventHandlers: i9, provide: n22, decorations: r2 } = e4 || {};
    return new s33(Cn++, t5, i9, (o4) => {
      let l11 = [
        bt.of(o4)
      ];
      return r2 && l11.push(Ht.of((h3) => {
        let a2 = h3.plugin(o4);
        return a2 ? r2(a2) : C2.none;
      })), n22 && l11.push(n22(o4)), l11;
    });
  }
  static fromClass(t5, e4) {
    return s33.define((i9) => new t5(i9), e4);
  }
};
var Mt = class {
  constructor(t5) {
    this.spec = t5, this.mustUpdate = null, this.value = null;
  }
  update(t5) {
    if (this.value) {
      if (this.mustUpdate) {
        let e4 = this.mustUpdate;
        if (this.mustUpdate = null, this.value.update) try {
          this.value.update(e4);
        } catch (i9) {
          if (Z2(e4.state, i9, "CodeMirror plugin crashed"), this.value.destroy) try {
            this.value.destroy();
          } catch {
          }
          this.deactivate();
        }
      }
    } else if (this.spec) try {
      this.value = this.spec.create(t5);
    } catch (e4) {
      Z2(t5.state, e4, "CodeMirror plugin crashed"), this.deactivate();
    }
    return this;
  }
  destroy(t5) {
    var e4;
    if (!((e4 = this.value) === null || e4 === void 0) && e4.destroy) try {
      this.value.destroy();
    } catch (i9) {
      Z2(t5.state, i9, "CodeMirror plugin crashed");
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
  constructor(t5, e4, i9, n22) {
    this.fromA = t5, this.toA = e4, this.fromB = i9, this.toB = n22;
  }
  join(t5) {
    return new s34(Math.min(this.fromA, t5.fromA), Math.max(this.toA, t5.toA), Math.min(this.fromB, t5.fromB), Math.max(this.toB, t5.toB));
  }
  addToSet(t5) {
    let e4 = t5.length, i9 = this;
    for (; e4 > 0; e4--) {
      let n22 = t5[e4 - 1];
      if (!(n22.fromA > i9.toA)) {
        if (n22.toA < i9.fromA) break;
        i9 = i9.join(n22), t5.splice(e4 - 1, 1);
      }
    }
    return t5.splice(e4, 0, i9), t5;
  }
  static extendWithRanges(t5, e4) {
    if (e4.length == 0) return t5;
    let i9 = [];
    for (let n22 = 0, r2 = 0, o4 = 0, l11 = 0; ; n22++) {
      let h3 = n22 == t5.length ? null : t5[n22], a2 = o4 - l11, c4 = h3 ? h3.fromB : 1e9;
      for (; r2 < e4.length && e4[r2] < c4; ) {
        let f2 = e4[r2], u5 = e4[r2 + 1], d5 = Math.max(l11, f2), p5 = Math.min(c4, u5);
        if (d5 <= p5 && new s34(d5 + a2, p5 + a2, d5, p5).addToSet(i9), u5 > c4) break;
        r2 += 2;
      }
      if (!h3) return i9;
      new s34(h3.fromA, h3.toA, h3.fromB, h3.toB).addToSet(i9), o4 = h3.toA, l11 = h3.toB;
    }
  }
};
var ie2 = class s35 {
  constructor(t5, e4, i9) {
    this.view = t5, this.state = e4, this.transactions = i9, this.flags = 0, this.startState = t5.state, this.changes = P.empty(this.startState.doc.length);
    for (let o4 of i9) this.changes = this.changes.compose(o4.changes);
    let n22 = [];
    this.changes.iterChangedRanges((o4, l11, h3, a2) => n22.push(new it2(o4, l11, h3, a2))), this.changedRanges = n22;
    let r2 = t5.hasFocus;
    r2 != t5.inputState.notifiedFocused && (t5.inputState.notifiedFocused = r2, this.flags |= 1);
  }
  static create(t5, e4, i9) {
    return new s35(t5, e4, i9);
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
    return this.transactions.some((t5) => t5.selection);
  }
  get empty() {
    return this.flags == 0 && this.transactions.length == 0;
  }
};
var O2 = function(s99) {
  return s99[s99.LTR = 0] = "LTR", s99[s99.RTL = 1] = "RTL", s99;
}(O2 || (O2 = {}));
var Fe2 = O2.LTR;
var Mn = O2.RTL;
function Bs(s99) {
  let t5 = [];
  for (let e4 = 0; e4 < s99.length; e4++) t5.push(1 << +s99[e4]);
  return t5;
}
var kn = Bs("88888888888888888888888888888888888666888888787833333333337888888000000000000000000000000008888880000000000000000000000000088888888888888888888888888888888888887866668888088888663380888308888800000000000000000000000800000000000000000000000000000008");
var An = Bs("4444448826627288999999999992222222222222222222222222222222222222222222222229999999999999999999994444444444644222822222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222999999949999999229989999223333333333");
var Ie2 = /* @__PURE__ */ Object.create(null);
var F2 = [];
for (let s99 of [
  "()",
  "[]",
  "{}"
]) {
  let t5 = s99.charCodeAt(0), e4 = s99.charCodeAt(1);
  Ie2[t5] = e4, Ie2[e4] = -t5;
}
function Dn(s99) {
  return s99 <= 247 ? kn[s99] : 1424 <= s99 && s99 <= 1524 ? 2 : 1536 <= s99 && s99 <= 1785 ? An[s99 - 1536] : 1774 <= s99 && s99 <= 2220 ? 4 : 8192 <= s99 && s99 <= 8203 || s99 == 8204 ? 256 : 1;
}
var Tn = /[\u0590-\u05f4\u0600-\u06ff\u0700-\u08ac]/;
var Q2 = class {
  constructor(t5, e4, i9) {
    this.from = t5, this.to = e4, this.level = i9;
  }
  get dir() {
    return this.level % 2 ? Mn : Fe2;
  }
  side(t5, e4) {
    return this.dir == e4 == t5 ? this.to : this.from;
  }
  static find(t5, e4, i9, n22) {
    let r2 = -1;
    for (let o4 = 0; o4 < t5.length; o4++) {
      let l11 = t5[o4];
      if (l11.from <= e4 && l11.to >= e4) {
        if (l11.level == i9) return o4;
        (r2 < 0 || (n22 != 0 ? n22 < 0 ? l11.from < e4 : l11.to > e4 : t5[r2].level > l11.level)) && (r2 = o4);
      }
    }
    if (r2 < 0) throw new RangeError("Index out of range");
    return r2;
  }
};
var T3 = [];
function Hs(s99, t5) {
  let e4 = s99.length, i9 = t5 == Fe2 ? 1 : 2, n22 = t5 == Fe2 ? 2 : 1;
  if (!s99 || i9 == 1 && !Tn.test(s99)) return Ps(e4);
  for (let o4 = 0, l11 = i9, h3 = i9; o4 < e4; o4++) {
    let a2 = Dn(s99.charCodeAt(o4));
    a2 == 512 ? a2 = l11 : a2 == 8 && h3 == 4 && (a2 = 16), T3[o4] = a2 == 4 ? 2 : a2, a2 & 7 && (h3 = a2), l11 = a2;
  }
  for (let o4 = 0, l11 = i9, h3 = i9; o4 < e4; o4++) {
    let a2 = T3[o4];
    if (a2 == 128) o4 < e4 - 1 && l11 == T3[o4 + 1] && l11 & 24 ? a2 = T3[o4] = l11 : T3[o4] = 256;
    else if (a2 == 64) {
      let c4 = o4 + 1;
      for (; c4 < e4 && T3[c4] == 64; ) c4++;
      let f2 = o4 && l11 == 8 || c4 < e4 && T3[c4] == 8 ? h3 == 1 ? 1 : 8 : 256;
      for (let u5 = o4; u5 < c4; u5++) T3[u5] = f2;
      o4 = c4 - 1;
    } else a2 == 8 && h3 == 1 && (T3[o4] = 1);
    l11 = a2, a2 & 7 && (h3 = a2);
  }
  for (let o4 = 0, l11 = 0, h3 = 0, a2, c4, f2; o4 < e4; o4++) if (c4 = Ie2[a2 = s99.charCodeAt(o4)]) if (c4 < 0) {
    for (let u5 = l11 - 3; u5 >= 0; u5 -= 3) if (F2[u5 + 1] == -c4) {
      let d5 = F2[u5 + 2], p5 = d5 & 2 ? i9 : d5 & 4 ? d5 & 1 ? n22 : i9 : 0;
      p5 && (T3[o4] = T3[F2[u5]] = p5), l11 = u5;
      break;
    }
  } else {
    if (F2.length == 189) break;
    F2[l11++] = o4, F2[l11++] = a2, F2[l11++] = h3;
  }
  else if ((f2 = T3[o4]) == 2 || f2 == 1) {
    let u5 = f2 == i9;
    h3 = u5 ? 0 : 1;
    for (let d5 = l11 - 3; d5 >= 0; d5 -= 3) {
      let p5 = F2[d5 + 2];
      if (p5 & 2) break;
      if (u5) F2[d5 + 2] |= 2;
      else {
        if (p5 & 4) break;
        F2[d5 + 2] |= 4;
      }
    }
  }
  for (let o4 = 0; o4 < e4; o4++) if (T3[o4] == 256) {
    let l11 = o4 + 1;
    for (; l11 < e4 && T3[l11] == 256; ) l11++;
    let h3 = (o4 ? T3[o4 - 1] : i9) == 1, a2 = (l11 < e4 ? T3[l11] : i9) == 1, c4 = h3 == a2 ? h3 ? 1 : 2 : i9;
    for (let f2 = o4; f2 < l11; f2++) T3[f2] = c4;
    o4 = l11 - 1;
  }
  let r2 = [];
  if (i9 == 1) for (let o4 = 0; o4 < e4; ) {
    let l11 = o4, h3 = T3[o4++] != 1;
    for (; o4 < e4 && h3 == (T3[o4] != 1); ) o4++;
    if (h3) for (let a2 = o4; a2 > l11; ) {
      let c4 = a2, f2 = T3[--a2] != 2;
      for (; a2 > l11 && f2 == (T3[a2 - 1] != 2); ) a2--;
      r2.push(new Q2(a2, c4, f2 ? 2 : 1));
    }
    else r2.push(new Q2(l11, o4, 0));
  }
  else for (let o4 = 0; o4 < e4; ) {
    let l11 = o4, h3 = T3[o4++] == 2;
    for (; o4 < e4 && h3 == (T3[o4] == 2); ) o4++;
    r2.push(new Q2(l11, o4, h3 ? 1 : 2));
  }
  return r2;
}
function Ps(s99) {
  return [
    new Q2(0, s99, 0)
  ];
}
var Vs = "";
function Ns(s99, t5, e4, i9, n22) {
  var r2;
  let o4 = i9.head - s99.from, l11 = -1;
  if (o4 == 0) {
    if (!n22 || !s99.length) return null;
    t5[0].level != e4 && (o4 = t5[0].side(false, e4), l11 = 0);
  } else if (o4 == s99.length) {
    if (n22) return null;
    let u5 = t5[t5.length - 1];
    u5.level != e4 && (o4 = u5.side(true, e4), l11 = t5.length - 1);
  }
  l11 < 0 && (l11 = Q2.find(t5, o4, (r2 = i9.bidiLevel) !== null && r2 !== void 0 ? r2 : -1, i9.assoc));
  let h3 = t5[l11];
  o4 == h3.side(n22, e4) && (h3 = t5[l11 += n22 ? 1 : -1], o4 = h3.side(!n22, e4));
  let a2 = n22 == (h3.dir == e4), c4 = _(s99.text, o4, a2);
  if (Vs = s99.text.slice(Math.min(o4, c4), Math.max(o4, c4)), c4 != h3.side(n22, e4)) return x.cursor(c4 + s99.from, a2 ? -1 : 1, h3.level);
  let f2 = l11 == (n22 ? t5.length - 1 : 0) ? null : t5[l11 + (n22 ? 1 : -1)];
  return !f2 && h3.level != e4 ? x.cursor(n22 ? s99.to : s99.from, n22 ? -1 : 1, e4) : f2 && f2.level < h3.level ? x.cursor(f2.side(!n22, e4) + s99.from, n22 ? 1 : -1, f2.level) : x.cursor(c4 + s99.from, n22 ? -1 : 1, h3.level);
}
var X2 = "\uFFFF";
var se2 = class {
  constructor(t5, e4) {
    this.points = t5, this.text = "", this.lineSeparator = e4.facet(I.lineSeparator);
  }
  append(t5) {
    this.text += t5;
  }
  lineBreak() {
    this.text += X2;
  }
  readRange(t5, e4) {
    if (!t5) return this;
    let i9 = t5.parentNode;
    for (let n22 = t5; ; ) {
      this.findPointBefore(i9, n22), this.readNode(n22);
      let r2 = n22.nextSibling;
      if (r2 == e4) break;
      let o4 = R2.get(n22), l11 = R2.get(r2);
      (o4 && l11 ? o4.breakAfter : (o4 ? o4.breakAfter : Ti(n22)) || Ti(r2) && (n22.nodeName != "BR" || n22.cmIgnore)) && this.lineBreak(), n22 = r2;
    }
    return this.findPointBefore(i9, e4), this;
  }
  readTextNode(t5) {
    let e4 = t5.nodeValue;
    for (let i9 of this.points) i9.node == t5 && (i9.pos = this.text.length + Math.min(i9.offset, e4.length));
    for (let i9 = 0, n22 = this.lineSeparator ? null : /\r\n?|\n/g; ; ) {
      let r2 = -1, o4 = 1, l11;
      if (this.lineSeparator ? (r2 = e4.indexOf(this.lineSeparator, i9), o4 = this.lineSeparator.length) : (l11 = n22.exec(e4)) && (r2 = l11.index, o4 = l11[0].length), this.append(e4.slice(i9, r2 < 0 ? e4.length : r2)), r2 < 0) break;
      if (this.lineBreak(), o4 > 1) for (let h3 of this.points) h3.node == t5 && h3.pos > this.text.length && (h3.pos -= o4 - 1);
      i9 = r2 + o4;
    }
  }
  readNode(t5) {
    if (t5.cmIgnore) return;
    let e4 = R2.get(t5), i9 = e4 && e4.overrideDOMText;
    if (i9 != null) {
      this.findPointInside(t5, i9.length);
      for (let n22 = i9.iter(); !n22.next().done; ) n22.lineBreak ? this.lineBreak() : this.append(n22.value);
    } else t5.nodeType == 3 ? this.readTextNode(t5) : t5.nodeName == "BR" ? t5.nextSibling && this.lineBreak() : t5.nodeType == 1 && this.readRange(t5.firstChild, null);
  }
  findPointBefore(t5, e4) {
    for (let i9 of this.points) i9.node == t5 && t5.childNodes[i9.offset] == e4 && (i9.pos = this.text.length);
  }
  findPointInside(t5, e4) {
    for (let i9 of this.points) (t5.nodeType == 3 ? i9.node == t5 : t5.contains(i9.node)) && (i9.pos = this.text.length + Math.min(e4, i9.offset));
  }
};
function Ti(s99) {
  return s99.nodeType == 1 && /^(DIV|P|LI|UL|OL|BLOCKQUOTE|DD|DT|H\d|SECTION|PRE)$/.test(s99.nodeName);
}
var ne2 = class {
  constructor(t5, e4) {
    this.node = t5, this.offset = e4, this.pos = -1;
  }
};
var re2 = class extends R2 {
  constructor(t5) {
    super(), this.view = t5, this.compositionDeco = C2.none, this.decorations = [], this.dynamicDecorationMap = [], this.minWidth = 0, this.minWidthFrom = 0, this.minWidthTo = 0, this.impreciseAnchor = null, this.impreciseHead = null, this.forceSelection = false, this.lastUpdate = Date.now(), this.setDOM(t5.contentDOM), this.children = [
      new N2()
    ], this.children[0].setParent(this), this.updateDeco(), this.updateInner([
      new it2(0, 0, 0, t5.state.doc.length)
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
  update(t5) {
    let e4 = t5.changedRanges;
    this.minWidth > 0 && e4.length && (e4.every(({ fromA: o4, toA: l11 }) => l11 < this.minWidthFrom || o4 > this.minWidthTo) ? (this.minWidthFrom = t5.changes.mapPos(this.minWidthFrom, 1), this.minWidthTo = t5.changes.mapPos(this.minWidthTo, 1)) : this.minWidth = this.minWidthFrom = this.minWidthTo = 0), this.view.inputState.composing < 0 ? this.compositionDeco = C2.none : (t5.transactions.length || this.dirty) && (this.compositionDeco = Rn(this.view, t5.changes)), (g2.ie || g2.chrome) && !this.compositionDeco.size && t5 && t5.state.doc.lines != t5.startState.doc.lines && (this.forceSelection = true);
    let i9 = this.decorations, n22 = this.updateDeco(), r2 = En(i9, n22, t5.changes);
    return e4 = it2.extendWithRanges(e4, r2), this.dirty == 0 && e4.length == 0 ? false : (this.updateInner(e4, t5.startState.doc.length), t5.transactions.length && (this.lastUpdate = Date.now()), true);
  }
  updateInner(t5, e4) {
    this.view.viewState.mustMeasureContent = true, this.updateChildren(t5, e4);
    let { observer: i9 } = this.view;
    i9.ignore(() => {
      this.dom.style.height = this.view.viewState.contentHeight + "px", this.dom.style.flexBasis = this.minWidth ? this.minWidth + "px" : "";
      let r2 = g2.chrome || g2.ios ? {
        node: i9.selectionRange.focusNode,
        written: false
      } : void 0;
      this.sync(r2), this.dirty = 0, r2 && (r2.written || i9.selectionRange.focusNode != r2.node) && (this.forceSelection = true), this.dom.style.height = "";
    });
    let n22 = [];
    if (this.view.viewport.from || this.view.viewport.to < this.view.state.doc.length) for (let r2 of this.children) r2 instanceof Bt && r2.widget instanceof oe2 && n22.push(r2.dom);
    i9.updateGaps(n22);
  }
  updateChildren(t5, e4) {
    let i9 = this.childCursor(e4);
    for (let n22 = t5.length - 1; ; n22--) {
      let r2 = n22 >= 0 ? t5[n22] : null;
      if (!r2) break;
      let { fromA: o4, toA: l11, fromB: h3, toB: a2 } = r2, { content: c4, breakAtStart: f2, openStart: u5, openEnd: d5 } = We2.build(this.view.state.doc, h3, a2, this.decorations, this.dynamicDecorationMap), { i: p5, off: m9 } = i9.findPos(l11, 1), { i: b9, off: y10 } = i9.findPos(o4, -1);
      ms(this, b9, y10, p5, m9, c4, f2, u5, d5);
    }
  }
  updateSelection(t5 = false, e4 = false) {
    if (t5 && this.view.observer.readSelectionRange(), !(e4 || this.mayControlSelection()) || g2.ios && this.view.inputState.rapidCompositionStart) return;
    let i9 = this.forceSelection;
    this.forceSelection = false;
    let n22 = this.view.state.selection.main, r2 = this.domAtPos(n22.anchor), o4 = n22.empty ? r2 : this.domAtPos(n22.head);
    if (g2.gecko && n22.empty && On(r2)) {
      let h3 = document.createTextNode("");
      this.view.observer.ignore(() => r2.node.insertBefore(h3, r2.node.childNodes[r2.offset] || null)), r2 = o4 = new B2(h3, 0), i9 = true;
    }
    let l11 = this.view.observer.selectionRange;
    (i9 || !l11.focusNode || !Ut(r2.node, r2.offset, l11.anchorNode, l11.anchorOffset) || !Ut(o4.node, o4.offset, l11.focusNode, l11.focusOffset)) && (this.view.observer.ignore(() => {
      g2.android && g2.chrome && this.dom.contains(l11.focusNode) && Bn(l11.focusNode, this.dom) && (this.dom.blur(), this.dom.focus({
        preventScroll: true
      }));
      let h3 = Yt(this.root);
      if (n22.empty) {
        if (g2.gecko) {
          let a2 = Ln(r2.node, r2.offset);
          if (a2 && a2 != 3) {
            let c4 = zs(r2.node, r2.offset, a2 == 1 ? 1 : -1);
            c4 && (r2 = new B2(c4, a2 == 1 ? 0 : c4.nodeValue.length));
          }
        }
        h3.collapse(r2.node, r2.offset), n22.bidiLevel != null && l11.cursorBidiLevel != null && (l11.cursorBidiLevel = n22.bidiLevel);
      } else if (h3.extend) h3.collapse(r2.node, r2.offset), h3.extend(o4.node, o4.offset);
      else {
        let a2 = document.createRange();
        n22.anchor > n22.head && ([r2, o4] = [
          o4,
          r2
        ]), a2.setEnd(o4.node, o4.offset), a2.setStart(r2.node, r2.offset), h3.removeAllRanges(), h3.addRange(a2);
      }
    }), this.view.observer.setSelectionRange(r2, o4)), this.impreciseAnchor = r2.precise ? null : new B2(l11.anchorNode, l11.anchorOffset), this.impreciseHead = o4.precise ? null : new B2(l11.focusNode, l11.focusOffset);
  }
  enforceCursorAssoc() {
    if (this.compositionDeco.size) return;
    let t5 = this.view.state.selection.main, e4 = Yt(this.root);
    if (!t5.empty || !t5.assoc || !e4.modify) return;
    let i9 = N2.find(this, t5.head);
    if (!i9) return;
    let n22 = i9.posAtStart;
    if (t5.head == n22 || t5.head == n22 + i9.length) return;
    let r2 = this.coordsAt(t5.head, -1), o4 = this.coordsAt(t5.head, 1);
    if (!r2 || !o4 || r2.bottom > o4.top) return;
    let l11 = this.domAtPos(t5.head + t5.assoc);
    e4.collapse(l11.node, l11.offset), e4.modify("move", t5.assoc < 0 ? "forward" : "backward", "lineboundary");
  }
  mayControlSelection() {
    return this.view.state.facet(Nt) ? this.root.activeElement == this.dom : De2(this.dom, this.view.observer.selectionRange);
  }
  nearest(t5) {
    for (let e4 = t5; e4; ) {
      let i9 = R2.get(e4);
      if (i9 && i9.rootView == this) return i9;
      e4 = e4.parentNode;
    }
    return null;
  }
  posFromDOM(t5, e4) {
    let i9 = this.nearest(t5);
    if (!i9) throw new RangeError("Trying to find position for a DOM position outside of the document");
    return i9.localPosFromDOM(t5, e4) + i9.posAtStart;
  }
  domAtPos(t5) {
    let { i: e4, off: i9 } = this.childCursor().findPos(t5, -1);
    for (; e4 < this.children.length - 1; ) {
      let n22 = this.children[e4];
      if (i9 < n22.length || n22 instanceof N2) break;
      e4++, i9 = 0;
    }
    return this.children[e4].domAtPos(i9);
  }
  coordsAt(t5, e4) {
    for (let i9 = this.length, n22 = this.children.length - 1; ; n22--) {
      let r2 = this.children[n22], o4 = i9 - r2.breakAfter - r2.length;
      if (t5 > o4 || t5 == o4 && r2.type != D2.WidgetBefore && r2.type != D2.WidgetAfter && (!n22 || e4 == 2 || this.children[n22 - 1].breakAfter || this.children[n22 - 1].type == D2.WidgetBefore && e4 > -2)) return r2.coordsAt(t5 - o4, e4);
      i9 = o4;
    }
  }
  measureVisibleLineHeights(t5) {
    let e4 = [], { from: i9, to: n22 } = t5, r2 = this.view.contentDOM.clientWidth, o4 = r2 > Math.max(this.view.scrollDOM.clientWidth, this.minWidth) + 1, l11 = -1, h3 = this.view.textDirection == O2.LTR;
    for (let a2 = 0, c4 = 0; c4 < this.children.length; c4++) {
      let f2 = this.children[c4], u5 = a2 + f2.length;
      if (u5 > n22) break;
      if (a2 >= i9) {
        let d5 = f2.dom.getBoundingClientRect();
        if (e4.push(d5.height), o4) {
          let p5 = f2.dom.lastChild, m9 = p5 ? Tt(p5) : [];
          if (m9.length) {
            let b9 = m9[m9.length - 1], y10 = h3 ? b9.right - d5.left : d5.right - b9.left;
            y10 > l11 && (l11 = y10, this.minWidth = r2, this.minWidthFrom = a2, this.minWidthTo = u5);
          }
        }
      }
      a2 = u5 + f2.breakAfter;
    }
    return e4;
  }
  textDirectionAt(t5) {
    let { i: e4 } = this.childPos(t5, 1);
    return getComputedStyle(this.children[e4].dom).direction == "rtl" ? O2.RTL : O2.LTR;
  }
  measureTextSize() {
    for (let n22 of this.children) if (n22 instanceof N2) {
      let r2 = n22.measureTextSize();
      if (r2) return r2;
    }
    let t5 = document.createElement("div"), e4, i9;
    return t5.className = "cm-line", t5.textContent = "abc def ghi jkl mno pqr stu", this.view.observer.ignore(() => {
      this.dom.appendChild(t5);
      let n22 = Tt(t5.firstChild)[0];
      e4 = t5.getBoundingClientRect().height, i9 = n22 ? n22.width / 27 : 7, t5.remove();
    }), {
      lineHeight: e4,
      charWidth: i9
    };
  }
  childCursor(t5 = this.length) {
    let e4 = this.children.length;
    return e4 && (t5 -= this.children[--e4].length), new Jt(this.children, t5, e4);
  }
  computeBlockGapDeco() {
    let t5 = [], e4 = this.view.viewState;
    for (let i9 = 0, n22 = 0; ; n22++) {
      let r2 = n22 == e4.viewports.length ? null : e4.viewports[n22], o4 = r2 ? r2.from - 1 : this.length;
      if (o4 > i9) {
        let l11 = e4.lineBlockAt(o4).bottom - e4.lineBlockAt(i9).top;
        t5.push(C2.replace({
          widget: new oe2(l11),
          block: true,
          inclusive: true,
          isBlockGap: true
        }).range(i9, o4));
      }
      if (!r2) break;
      i9 = r2.to + 1;
    }
    return C2.set(t5);
  }
  updateDeco() {
    let t5 = this.view.state.facet(Ht).map((e4, i9) => (this.dynamicDecorationMap[i9] = typeof e4 == "function") ? e4(this.view) : e4);
    for (let e4 = t5.length; e4 < t5.length + 3; e4++) this.dynamicDecorationMap[e4] = false;
    return this.decorations = [
      ...t5,
      this.compositionDeco,
      this.computeBlockGapDeco(),
      this.view.viewState.lineGapDeco
    ];
  }
  scrollIntoView(t5) {
    let { range: e4 } = t5, i9 = this.coordsAt(e4.head, e4.empty ? e4.assoc : e4.head > e4.anchor ? -1 : 1), n22;
    if (!i9) return;
    !e4.empty && (n22 = this.coordsAt(e4.anchor, e4.anchor > e4.head ? -1 : 1)) && (i9 = {
      left: Math.min(i9.left, n22.left),
      top: Math.min(i9.top, n22.top),
      right: Math.max(i9.right, n22.right),
      bottom: Math.max(i9.bottom, n22.bottom)
    });
    let r2 = 0, o4 = 0, l11 = 0, h3 = 0;
    for (let c4 of this.view.state.facet(Es).map((f2) => f2(this.view))) if (c4) {
      let { left: f2, right: u5, top: d5, bottom: p5 } = c4;
      f2 != null && (r2 = Math.max(r2, f2)), u5 != null && (o4 = Math.max(o4, u5)), d5 != null && (l11 = Math.max(l11, d5)), p5 != null && (h3 = Math.max(h3, p5));
    }
    let a2 = {
      left: i9.left - r2,
      top: i9.top - l11,
      right: i9.right + o4,
      bottom: i9.bottom + h3
    };
    yn(this.view.scrollDOM, a2, e4.head < e4.anchor ? -1 : 1, t5.x, t5.y, t5.xMargin, t5.yMargin, this.view.textDirection == O2.LTR);
  }
};
function On(s99) {
  return s99.node.nodeType == 1 && s99.node.firstChild && (s99.offset == 0 || s99.node.childNodes[s99.offset - 1].contentEditable == "false") && (s99.offset == s99.node.childNodes.length || s99.node.childNodes[s99.offset].contentEditable == "false");
}
var oe2 = class extends K2 {
  constructor(t5) {
    super(), this.height = t5;
  }
  toDOM() {
    let t5 = document.createElement("div");
    return this.updateDOM(t5), t5;
  }
  eq(t5) {
    return t5.height == this.height;
  }
  updateDOM(t5) {
    return t5.style.height = this.height + "px", true;
  }
  get estimatedHeight() {
    return this.height;
  }
};
function Ws(s99) {
  let t5 = s99.observer.selectionRange, e4 = t5.focusNode && zs(t5.focusNode, t5.focusOffset, 0);
  if (!e4) return null;
  let i9 = s99.docView.nearest(e4);
  if (!i9) return null;
  if (i9 instanceof N2) {
    let n22 = e4;
    for (; n22.parentNode != i9.dom; ) n22 = n22.parentNode;
    let r2 = n22.previousSibling;
    for (; r2 && !R2.get(r2); ) r2 = r2.previousSibling;
    let o4 = r2 ? R2.get(r2).posAtEnd : i9.posAtStart;
    return {
      from: o4,
      to: o4,
      node: n22,
      text: e4
    };
  } else {
    for (; ; ) {
      let { parent: r2 } = i9;
      if (!r2) return null;
      if (r2 instanceof N2) break;
      i9 = r2;
    }
    let n22 = i9.posAtStart;
    return {
      from: n22,
      to: n22 + i9.length,
      node: i9.dom,
      text: e4
    };
  }
}
function Rn(s99, t5) {
  let e4 = Ws(s99);
  if (!e4) return C2.none;
  let { from: i9, to: n22, node: r2, text: o4 } = e4, l11 = t5.mapPos(i9, 1), h3 = Math.max(l11, t5.mapPos(n22, -1)), { state: a2 } = s99, c4 = r2.nodeType == 3 ? r2.nodeValue : new se2([], a2).readRange(r2.firstChild, null).text;
  if (h3 - l11 < c4.length) if (a2.doc.sliceString(l11, Math.min(a2.doc.length, l11 + c4.length), X2) == c4) h3 = l11 + c4.length;
  else if (a2.doc.sliceString(Math.max(0, h3 - c4.length), h3, X2) == c4) l11 = h3 - c4.length;
  else return C2.none;
  else if (a2.doc.sliceString(l11, h3, X2) != c4) return C2.none;
  let f2 = R2.get(r2);
  return f2 instanceof Zt ? f2 = f2.widget.topView : f2 && (f2.parent = null), C2.set(C2.replace({
    widget: new qe2(r2, o4, f2),
    inclusive: true
  }).range(l11, h3));
}
var qe2 = class extends K2 {
  constructor(t5, e4, i9) {
    super(), this.top = t5, this.text = e4, this.topView = i9;
  }
  eq(t5) {
    return this.top == t5.top && this.text == t5.text;
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
function zs(s99, t5, e4) {
  for (; ; ) {
    if (s99.nodeType == 3) return s99;
    if (s99.nodeType == 1 && t5 > 0 && e4 <= 0) s99 = s99.childNodes[t5 - 1], t5 = Xt(s99);
    else if (s99.nodeType == 1 && t5 < s99.childNodes.length && e4 >= 0) s99 = s99.childNodes[t5], t5 = 0;
    else return null;
  }
}
function Ln(s99, t5) {
  return s99.nodeType != 1 ? 0 : (t5 && s99.childNodes[t5 - 1].contentEditable == "false" ? 1 : 0) | (t5 < s99.childNodes.length && s99.childNodes[t5].contentEditable == "false" ? 2 : 0);
}
var Ke2 = class {
  constructor() {
    this.changes = [];
  }
  compareRange(t5, e4) {
    Ne2(t5, e4, this.changes);
  }
  comparePoint(t5, e4) {
    Ne2(t5, e4, this.changes);
  }
};
function En(s99, t5, e4) {
  let i9 = new Ke2();
  return O.compare(s99, t5, e4, i9), i9.changes;
}
function Bn(s99, t5) {
  for (let e4 = s99; e4 && e4 != t5; e4 = e4.assignedSlot || e4.parentNode) if (e4.nodeType == 1 && e4.contentEditable == "false") return true;
  return false;
}
function Hn(s99, t5, e4 = 1) {
  let i9 = s99.charCategorizer(t5), n22 = s99.doc.lineAt(t5), r2 = t5 - n22.from;
  if (n22.length == 0) return x.cursor(t5);
  r2 == 0 ? e4 = 1 : r2 == n22.length && (e4 = -1);
  let o4 = r2, l11 = r2;
  e4 < 0 ? o4 = _(n22.text, r2, false) : l11 = _(n22.text, r2);
  let h3 = i9(n22.text.slice(o4, l11));
  for (; o4 > 0; ) {
    let a2 = _(n22.text, o4, false);
    if (i9(n22.text.slice(a2, o4)) != h3) break;
    o4 = a2;
  }
  for (; l11 < n22.length; ) {
    let a2 = _(n22.text, l11);
    if (i9(n22.text.slice(l11, a2)) != h3) break;
    l11 = a2;
  }
  return x.range(o4 + n22.from, l11 + n22.from);
}
function Pn(s99, t5) {
  return t5.left > s99 ? t5.left - s99 : Math.max(0, s99 - t5.right);
}
function Vn(s99, t5) {
  return t5.top > s99 ? t5.top - s99 : Math.max(0, s99 - t5.bottom);
}
function we2(s99, t5) {
  return s99.top < t5.bottom - 1 && s99.bottom > t5.top + 1;
}
function Oi(s99, t5) {
  return t5 < s99.top ? {
    top: t5,
    left: s99.left,
    right: s99.right,
    bottom: s99.bottom
  } : s99;
}
function Ri(s99, t5) {
  return t5 > s99.bottom ? {
    top: s99.top,
    left: s99.left,
    right: s99.right,
    bottom: t5
  } : s99;
}
function je2(s99, t5, e4) {
  let i9, n22, r2, o4, l11, h3, a2, c4;
  for (let d5 = s99.firstChild; d5; d5 = d5.nextSibling) {
    let p5 = Tt(d5);
    for (let m9 = 0; m9 < p5.length; m9++) {
      let b9 = p5[m9];
      n22 && we2(n22, b9) && (b9 = Oi(Ri(b9, n22.bottom), n22.top));
      let y10 = Pn(t5, b9), k13 = Vn(e4, b9);
      if (y10 == 0 && k13 == 0) return d5.nodeType == 3 ? Li(d5, t5, e4) : je2(d5, t5, e4);
      (!i9 || o4 > k13 || o4 == k13 && r2 > y10) && (i9 = d5, n22 = b9, r2 = y10, o4 = k13), y10 == 0 ? e4 > b9.bottom && (!a2 || a2.bottom < b9.bottom) ? (l11 = d5, a2 = b9) : e4 < b9.top && (!c4 || c4.top > b9.top) && (h3 = d5, c4 = b9) : a2 && we2(a2, b9) ? a2 = Ri(a2, b9.bottom) : c4 && we2(c4, b9) && (c4 = Oi(c4, b9.top));
    }
  }
  if (a2 && a2.bottom >= e4 ? (i9 = l11, n22 = a2) : c4 && c4.top <= e4 && (i9 = h3, n22 = c4), !i9) return {
    node: s99,
    offset: 0
  };
  let f2 = Math.max(n22.left, Math.min(n22.right, t5));
  if (i9.nodeType == 3) return Li(i9, f2, e4);
  if (!r2 && i9.contentEditable == "true") return je2(i9, f2, e4);
  let u5 = Array.prototype.indexOf.call(s99.childNodes, i9) + (t5 >= (n22.left + n22.right) / 2 ? 1 : 0);
  return {
    node: s99,
    offset: u5
  };
}
function Li(s99, t5, e4) {
  let i9 = s99.nodeValue.length, n22 = -1, r2 = 1e9, o4 = 0;
  for (let l11 = 0; l11 < i9; l11++) {
    let h3 = Ot(s99, l11, l11 + 1).getClientRects();
    for (let a2 = 0; a2 < h3.length; a2++) {
      let c4 = h3[a2];
      if (c4.top == c4.bottom) continue;
      o4 || (o4 = t5 - c4.left);
      let f2 = (c4.top > e4 ? c4.top - e4 : e4 - c4.bottom) - 1;
      if (c4.left - 1 <= t5 && c4.right + 1 >= t5 && f2 < r2) {
        let u5 = t5 >= (c4.left + c4.right) / 2, d5 = u5;
        if ((g2.chrome || g2.gecko) && Ot(s99, l11).getBoundingClientRect().left == c4.right && (d5 = !u5), f2 <= 0) return {
          node: s99,
          offset: l11 + (d5 ? 1 : 0)
        };
        n22 = l11 + (d5 ? 1 : 0), r2 = f2;
      }
    }
  }
  return {
    node: s99,
    offset: n22 > -1 ? n22 : o4 > 0 ? s99.nodeValue.length : 0
  };
}
function Fs(s99, { x: t5, y: e4 }, i9, n22 = -1) {
  var r2;
  let o4 = s99.contentDOM.getBoundingClientRect(), l11 = o4.top + s99.viewState.paddingTop, h3, { docHeight: a2 } = s99.viewState, c4 = e4 - l11;
  if (c4 < 0) return 0;
  if (c4 > a2) return s99.state.doc.length;
  for (let y10 = s99.defaultLineHeight / 2, k13 = false; h3 = s99.elementAtHeight(c4), h3.type != D2.Text; ) for (; c4 = n22 > 0 ? h3.bottom + y10 : h3.top - y10, !(c4 >= 0 && c4 <= a2); ) {
    if (k13) return i9 ? null : 0;
    k13 = true, n22 = -n22;
  }
  e4 = l11 + c4;
  let f2 = h3.from;
  if (f2 < s99.viewport.from) return s99.viewport.from == 0 ? 0 : i9 ? null : Ei(s99, o4, h3, t5, e4);
  if (f2 > s99.viewport.to) return s99.viewport.to == s99.state.doc.length ? s99.state.doc.length : i9 ? null : Ei(s99, o4, h3, t5, e4);
  let u5 = s99.dom.ownerDocument, d5 = s99.root.elementFromPoint ? s99.root : u5, p5 = d5.elementFromPoint(t5, e4);
  p5 && !s99.contentDOM.contains(p5) && (p5 = null), p5 || (t5 = Math.max(o4.left + 1, Math.min(o4.right - 1, t5)), p5 = d5.elementFromPoint(t5, e4), p5 && !s99.contentDOM.contains(p5) && (p5 = null));
  let m9, b9 = -1;
  if (p5 && ((r2 = s99.docView.nearest(p5)) === null || r2 === void 0 ? void 0 : r2.isEditable) != false) {
    if (u5.caretPositionFromPoint) {
      let y10 = u5.caretPositionFromPoint(t5, e4);
      y10 && ({ offsetNode: m9, offset: b9 } = y10);
    } else if (u5.caretRangeFromPoint) {
      let y10 = u5.caretRangeFromPoint(t5, e4);
      y10 && ({ startContainer: m9, startOffset: b9 } = y10, g2.safari && Nn(m9, b9, t5) && (m9 = void 0));
    }
  }
  if (!m9 || !s99.docView.dom.contains(m9)) {
    let y10 = N2.find(s99.docView, f2);
    if (!y10) return c4 > h3.top + h3.height / 2 ? h3.to : h3.from;
    ({ node: m9, offset: b9 } = je2(y10.dom, t5, e4));
  }
  return s99.docView.posFromDOM(m9, b9);
}
function Ei(s99, t5, e4, i9, n22) {
  let r2 = Math.round((i9 - t5.left) * s99.defaultCharacterWidth);
  if (s99.lineWrapping && e4.height > s99.defaultLineHeight * 1.5) {
    let l11 = Math.floor((n22 - e4.top) / s99.defaultLineHeight);
    r2 += l11 * s99.viewState.heightOracle.lineLength;
  }
  let o4 = s99.state.sliceDoc(e4.from, e4.to);
  return e4.from + at(o4, r2, s99.state.tabSize);
}
function Nn(s99, t5, e4) {
  let i9;
  if (s99.nodeType != 3 || t5 != (i9 = s99.nodeValue.length)) return false;
  for (let n22 = s99.nextSibling; n22; n22 = n22.nextSibling) if (n22.nodeType != 1 || n22.nodeName != "BR") return false;
  return Ot(s99, i9 - 1, i9).getBoundingClientRect().left > e4;
}
function Wn(s99, t5, e4, i9) {
  let n22 = s99.state.doc.lineAt(t5.head), r2 = !i9 || !s99.lineWrapping ? null : s99.coordsAtPos(t5.assoc < 0 && t5.head > n22.from ? t5.head - 1 : t5.head);
  if (r2) {
    let h3 = s99.dom.getBoundingClientRect(), a2 = s99.textDirectionAt(n22.from), c4 = s99.posAtCoords({
      x: e4 == (a2 == O2.LTR) ? h3.right - 1 : h3.left + 1,
      y: (r2.top + r2.bottom) / 2
    });
    if (c4 != null) return x.cursor(c4, e4 ? -1 : 1);
  }
  let o4 = N2.find(s99.docView, t5.head), l11 = o4 ? e4 ? o4.posAtEnd : o4.posAtStart : e4 ? n22.to : n22.from;
  return x.cursor(l11, e4 ? -1 : 1);
}
function Bi(s99, t5, e4, i9) {
  let n22 = s99.state.doc.lineAt(t5.head), r2 = s99.bidiSpans(n22), o4 = s99.textDirectionAt(n22.from);
  for (let l11 = t5, h3 = null; ; ) {
    let a2 = Ns(n22, r2, o4, l11, e4), c4 = Vs;
    if (!a2) {
      if (n22.number == (e4 ? s99.state.doc.lines : 1)) return l11;
      c4 = `
`, n22 = s99.state.doc.line(n22.number + (e4 ? 1 : -1)), r2 = s99.bidiSpans(n22), a2 = x.cursor(e4 ? n22.from : n22.to);
    }
    if (h3) {
      if (!h3(c4)) return l11;
    } else {
      if (!i9) return a2;
      h3 = i9(c4);
    }
    l11 = a2;
  }
}
function zn(s99, t5, e4) {
  let i9 = s99.state.charCategorizer(t5), n22 = i9(e4);
  return (r2) => {
    let o4 = i9(r2);
    return n22 == E.Space && (n22 = o4), n22 == o4;
  };
}
function Fn(s99, t5, e4, i9) {
  let n22 = t5.head, r2 = e4 ? 1 : -1;
  if (n22 == (e4 ? s99.state.doc.length : 0)) return x.cursor(n22, t5.assoc);
  let o4 = t5.goalColumn, l11, h3 = s99.contentDOM.getBoundingClientRect(), a2 = s99.coordsAtPos(n22), c4 = s99.documentTop;
  if (a2) o4 == null && (o4 = a2.left - h3.left), l11 = r2 < 0 ? a2.top : a2.bottom;
  else {
    let d5 = s99.viewState.lineBlockAt(n22);
    o4 == null && (o4 = Math.min(h3.right - h3.left, s99.defaultCharacterWidth * (n22 - d5.from))), l11 = (r2 < 0 ? d5.top : d5.bottom) + c4;
  }
  let f2 = h3.left + o4, u5 = i9 ?? s99.defaultLineHeight >> 1;
  for (let d5 = 0; ; d5 += 10) {
    let p5 = l11 + (u5 + d5) * r2, m9 = Fs(s99, {
      x: f2,
      y: p5
    }, false, r2);
    if (p5 < h3.top || p5 > h3.bottom || (r2 < 0 ? m9 < n22 : m9 > n22)) return x.cursor(m9, t5.assoc, void 0, o4);
  }
}
function ve2(s99, t5, e4) {
  let i9 = s99.state.facet(Ls).map((n22) => n22(s99));
  for (; ; ) {
    let n22 = false;
    for (let r2 of i9) r2.between(e4.from - 1, e4.from + 1, (o4, l11, h3) => {
      e4.from > o4 && e4.from < l11 && (e4 = t5.from > e4.from ? x.cursor(o4, 1) : x.cursor(l11, -1), n22 = true);
    });
    if (!n22) return e4;
  }
}
var Ge2 = class {
  constructor(t5) {
    this.lastKeyCode = 0, this.lastKeyTime = 0, this.chromeScrollHack = -1, this.pendingIOSKey = void 0, this.lastSelectionOrigin = null, this.lastSelectionTime = 0, this.lastEscPress = 0, this.lastContextMenu = 0, this.scrollHandlers = [], this.registeredEvents = [], this.customHandlers = [], this.composing = -1, this.compositionFirstChange = null, this.compositionEndedAt = 0, this.rapidCompositionStart = false, this.mouseSelection = null;
    for (let e4 in E2) {
      let i9 = E2[e4];
      t5.contentDOM.addEventListener(e4, (n22) => {
        !Hi(t5, n22) || this.ignoreDuringComposition(n22) || e4 == "keydown" && this.keydown(t5, n22) || (this.mustFlushObserver(n22) && t5.observer.forceFlush(), this.runCustomHandlers(e4, t5, n22) ? n22.preventDefault() : i9(t5, n22));
      }), this.registeredEvents.push(e4);
    }
    g2.chrome && g2.chrome_version >= 102 && t5.scrollDOM.addEventListener("wheel", () => {
      this.chromeScrollHack < 0 ? t5.contentDOM.style.pointerEvents = "none" : globalThis.clearTimeout(this.chromeScrollHack), this.chromeScrollHack = setTimeout(() => {
        this.chromeScrollHack = -1, t5.contentDOM.style.pointerEvents = "";
      }, 100);
    }, {
      passive: true
    }), this.notifiedFocused = t5.hasFocus, g2.safari && t5.contentDOM.addEventListener("input", () => null);
  }
  setSelectionOrigin(t5) {
    this.lastSelectionOrigin = t5, this.lastSelectionTime = Date.now();
  }
  ensureHandlers(t5, e4) {
    var i9;
    let n22;
    this.customHandlers = [];
    for (let r2 of e4) if (n22 = (i9 = r2.update(t5).spec) === null || i9 === void 0 ? void 0 : i9.domEventHandlers) {
      this.customHandlers.push({
        plugin: r2.value,
        handlers: n22
      });
      for (let o4 in n22) this.registeredEvents.indexOf(o4) < 0 && o4 != "scroll" && (this.registeredEvents.push(o4), t5.contentDOM.addEventListener(o4, (l11) => {
        Hi(t5, l11) && this.runCustomHandlers(o4, t5, l11) && l11.preventDefault();
      }));
    }
  }
  runCustomHandlers(t5, e4, i9) {
    for (let n22 of this.customHandlers) {
      let r2 = n22.handlers[t5];
      if (r2) try {
        if (r2.call(n22.plugin, i9, e4) || i9.defaultPrevented) return true;
      } catch (o4) {
        Z2(e4.state, o4);
      }
    }
    return false;
  }
  runScrollHandlers(t5, e4) {
    for (let i9 of this.customHandlers) {
      let n22 = i9.handlers.scroll;
      if (n22) try {
        n22.call(i9.plugin, e4, t5);
      } catch (r2) {
        Z2(t5.state, r2);
      }
    }
  }
  keydown(t5, e4) {
    if (this.lastKeyCode = e4.keyCode, this.lastKeyTime = Date.now(), e4.keyCode == 9 && Date.now() < this.lastEscPress + 2e3) return true;
    if (g2.android && g2.chrome && !e4.synthetic && (e4.keyCode == 13 || e4.keyCode == 8)) return t5.observer.delayAndroidKey(e4.key, e4.keyCode), true;
    let i9;
    return g2.ios && (i9 = Is.find((n22) => n22.keyCode == e4.keyCode)) && !(e4.ctrlKey || e4.altKey || e4.metaKey) && !e4.synthetic ? (this.pendingIOSKey = i9, setTimeout(() => this.flushIOSKey(t5), 250), true) : false;
  }
  flushIOSKey(t5) {
    let e4 = this.pendingIOSKey;
    return e4 ? (this.pendingIOSKey = void 0, Ct(t5.contentDOM, e4.key, e4.keyCode)) : false;
  }
  ignoreDuringComposition(t5) {
    return /^key/.test(t5.type) ? this.composing > 0 ? true : g2.safari && Date.now() - this.compositionEndedAt < 100 ? (this.compositionEndedAt = 0, true) : false : false;
  }
  mustFlushObserver(t5) {
    return t5.type == "keydown" && t5.keyCode != 229 || t5.type == "compositionend" && !g2.ios;
  }
  startMouseSelection(t5) {
    this.mouseSelection && this.mouseSelection.destroy(), this.mouseSelection = t5;
  }
  update(t5) {
    this.mouseSelection && this.mouseSelection.update(t5), t5.transactions.length && (this.lastKeyCode = this.lastSelectionTime = 0);
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
  constructor(t5, e4, i9, n22) {
    this.view = t5, this.style = i9, this.mustSelect = n22, this.lastEvent = e4;
    let r2 = t5.contentDOM.ownerDocument;
    r2.addEventListener("mousemove", this.move = this.move.bind(this)), r2.addEventListener("mouseup", this.up = this.up.bind(this)), this.extend = e4.shiftKey, this.multiple = t5.state.facet(I.allowMultipleSelections) && In(t5, e4), this.dragMove = qn(t5, e4), this.dragging = Kn(t5, e4) && yi(e4) == 1 ? null : false, this.dragging === false && (e4.preventDefault(), this.select(e4));
  }
  move(t5) {
    if (t5.buttons == 0) return this.destroy();
    this.dragging === false && this.select(this.lastEvent = t5);
  }
  up(t5) {
    this.dragging == null && this.select(this.lastEvent), this.dragging || t5.preventDefault(), this.destroy();
  }
  destroy() {
    let t5 = this.view.contentDOM.ownerDocument;
    t5.removeEventListener("mousemove", this.move), t5.removeEventListener("mouseup", this.up), this.view.inputState.mouseSelection = null;
  }
  select(t5) {
    let e4 = this.style.get(t5, this.extend, this.multiple);
    (this.mustSelect || !e4.eq(this.view.state.selection) || e4.main.assoc != this.view.state.selection.main.assoc) && this.view.dispatch({
      selection: e4,
      userEvent: "select.pointer",
      scrollIntoView: true
    }), this.mustSelect = false;
  }
  update(t5) {
    t5.docChanged && this.dragging && (this.dragging = this.dragging.map(t5.changes)), this.style.update(t5) && setTimeout(() => this.select(this.lastEvent), 20);
  }
};
function In(s99, t5) {
  let e4 = s99.state.facet(Ms);
  return e4.length ? e4[0](t5) : g2.mac ? t5.metaKey : t5.ctrlKey;
}
function qn(s99, t5) {
  let e4 = s99.state.facet(ks);
  return e4.length ? e4[0](t5) : g2.mac ? !t5.altKey : !t5.ctrlKey;
}
function Kn(s99, t5) {
  let { main: e4 } = s99.state.selection;
  if (e4.empty) return false;
  let i9 = Yt(s99.root);
  if (i9.rangeCount == 0) return true;
  let n22 = i9.getRangeAt(0).getClientRects();
  for (let r2 = 0; r2 < n22.length; r2++) {
    let o4 = n22[r2];
    if (o4.left <= t5.clientX && o4.right >= t5.clientX && o4.top <= t5.clientY && o4.bottom >= t5.clientY) return true;
  }
  return false;
}
function Hi(s99, t5) {
  if (!t5.bubbles) return true;
  if (t5.defaultPrevented) return false;
  for (let e4 = t5.target, i9; e4 != s99.contentDOM; e4 = e4.parentNode) if (!e4 || e4.nodeType == 11 || (i9 = R2.get(e4)) && i9.ignoreEvent(t5)) return false;
  return true;
}
var E2 = /* @__PURE__ */ Object.create(null);
var Ks = g2.ie && g2.ie_version < 15 || g2.ios && g2.webkit_version < 604;
function jn(s99) {
  let t5 = s99.dom.parentNode;
  if (!t5) return;
  let e4 = t5.appendChild(document.createElement("textarea"));
  e4.style.cssText = "position: fixed; left: -10000px; top: 10px", e4.focus(), setTimeout(() => {
    s99.focus(), e4.remove(), js(s99, e4.value);
  }, 50);
}
function js(s99, t5) {
  let { state: e4 } = s99, i9, n22 = 1, r2 = e4.toText(t5), o4 = r2.lines == e4.selection.ranges.length;
  if (_e2 != null && e4.selection.ranges.every((h3) => h3.empty) && _e2 == r2.toString()) {
    let h3 = -1;
    i9 = e4.changeByRange((a2) => {
      let c4 = e4.doc.lineAt(a2.from);
      if (c4.from == h3) return {
        range: a2
      };
      h3 = c4.from;
      let f2 = e4.toText((o4 ? r2.line(n22++).text : t5) + e4.lineBreak);
      return {
        changes: {
          from: c4.from,
          insert: f2
        },
        range: x.cursor(a2.from + f2.length)
      };
    });
  } else o4 ? i9 = e4.changeByRange((h3) => {
    let a2 = r2.line(n22++);
    return {
      changes: {
        from: h3.from,
        to: h3.to,
        insert: a2.text
      },
      range: x.cursor(h3.from + a2.length)
    };
  }) : i9 = e4.replaceSelection(r2);
  s99.dispatch(i9, {
    userEvent: "input.paste",
    scrollIntoView: true
  });
}
E2.keydown = (s99, t5) => {
  s99.inputState.setSelectionOrigin("select"), t5.keyCode == 27 ? s99.inputState.lastEscPress = Date.now() : qs.indexOf(t5.keyCode) < 0 && (s99.inputState.lastEscPress = 0);
};
var Gs = 0;
E2.touchstart = (s99, t5) => {
  Gs = Date.now(), s99.inputState.setSelectionOrigin("select.pointer");
};
E2.touchmove = (s99) => {
  s99.inputState.setSelectionOrigin("select.pointer");
};
E2.mousedown = (s99, t5) => {
  if (s99.observer.flush(), Gs > Date.now() - 2e3 && yi(t5) == 1) return;
  let e4 = null;
  for (let i9 of s99.state.facet(As)) if (e4 = i9(s99, t5), e4) break;
  if (!e4 && t5.button == 0 && (e4 = _n(s99, t5)), e4) {
    let i9 = s99.root.activeElement != s99.contentDOM;
    i9 && s99.observer.ignore(() => us(s99.contentDOM)), s99.inputState.startMouseSelection(new $e2(s99, t5, e4, i9));
  }
};
function Pi(s99, t5, e4, i9) {
  if (i9 == 1) return x.cursor(t5, e4);
  if (i9 == 2) return Hn(s99.state, t5, e4);
  {
    let n22 = N2.find(s99.docView, t5), r2 = s99.state.doc.lineAt(n22 ? n22.posAtEnd : t5), o4 = n22 ? n22.posAtStart : r2.from, l11 = n22 ? n22.posAtEnd : r2.to;
    return l11 < s99.state.doc.length && l11 == r2.to && l11++, x.range(o4, l11);
  }
}
var $s = (s99, t5) => s99 >= t5.top && s99 <= t5.bottom;
var Vi = (s99, t5, e4) => $s(t5, e4) && s99 >= e4.left && s99 <= e4.right;
function Gn(s99, t5, e4, i9) {
  let n22 = N2.find(s99.docView, t5);
  if (!n22) return 1;
  let r2 = t5 - n22.posAtStart;
  if (r2 == 0) return 1;
  if (r2 == n22.length) return -1;
  let o4 = n22.coordsAt(r2, -1);
  if (o4 && Vi(e4, i9, o4)) return -1;
  let l11 = n22.coordsAt(r2, 1);
  return l11 && Vi(e4, i9, l11) ? 1 : o4 && $s(i9, o4) ? -1 : 1;
}
function Ni(s99, t5) {
  let e4 = s99.posAtCoords({
    x: t5.clientX,
    y: t5.clientY
  }, false);
  return {
    pos: e4,
    bias: Gn(s99, e4, t5.clientX, t5.clientY)
  };
}
var $n = g2.ie && g2.ie_version <= 11;
var Wi = null;
var zi = 0;
var Fi = 0;
function yi(s99) {
  if (!$n) return s99.detail;
  let t5 = Wi, e4 = Fi;
  return Wi = s99, Fi = Date.now(), zi = !t5 || e4 > Date.now() - 400 && Math.abs(t5.clientX - s99.clientX) < 2 && Math.abs(t5.clientY - s99.clientY) < 2 ? (zi + 1) % 3 : 1;
}
function _n(s99, t5) {
  let e4 = Ni(s99, t5), i9 = yi(t5), n22 = s99.state.selection, r2 = e4, o4 = t5;
  return {
    update(l11) {
      l11.docChanged && (e4 && (e4.pos = l11.changes.mapPos(e4.pos)), n22 = n22.map(l11.changes), o4 = null);
    },
    get(l11, h3, a2) {
      let c4;
      if (o4 && l11.clientX == o4.clientX && l11.clientY == o4.clientY ? c4 = r2 : (c4 = r2 = Ni(s99, l11), o4 = l11), !c4 || !e4) return n22;
      let f2 = Pi(s99, c4.pos, c4.bias, i9);
      if (e4.pos != c4.pos && !h3) {
        let u5 = Pi(s99, e4.pos, e4.bias, i9), d5 = Math.min(u5.from, f2.from), p5 = Math.max(u5.to, f2.to);
        f2 = d5 < f2.from ? x.range(d5, p5) : x.range(p5, d5);
      }
      return h3 ? n22.replaceRange(n22.main.extend(f2.from, f2.to)) : a2 ? n22.addRange(f2) : x.create([
        f2
      ]);
    }
  };
}
E2.dragstart = (s99, t5) => {
  let { selection: { main: e4 } } = s99.state, { mouseSelection: i9 } = s99.inputState;
  i9 && (i9.dragging = e4), t5.dataTransfer && (t5.dataTransfer.setData("Text", s99.state.sliceDoc(e4.from, e4.to)), t5.dataTransfer.effectAllowed = "copyMove");
};
function Ii(s99, t5, e4, i9) {
  if (!e4) return;
  let n22 = s99.posAtCoords({
    x: t5.clientX,
    y: t5.clientY
  }, false);
  t5.preventDefault();
  let { mouseSelection: r2 } = s99.inputState, o4 = i9 && r2 && r2.dragging && r2.dragMove ? {
    from: r2.dragging.from,
    to: r2.dragging.to
  } : null, l11 = {
    from: n22,
    insert: e4
  }, h3 = s99.state.changes(o4 ? [
    o4,
    l11
  ] : l11);
  s99.focus(), s99.dispatch({
    changes: h3,
    selection: {
      anchor: h3.mapPos(n22, -1),
      head: h3.mapPos(n22, 1)
    },
    userEvent: o4 ? "move.drop" : "input.drop"
  });
}
E2.drop = (s99, t5) => {
  if (!t5.dataTransfer) return;
  if (s99.state.readOnly) return t5.preventDefault();
  let e4 = t5.dataTransfer.files;
  if (e4 && e4.length) {
    t5.preventDefault();
    let i9 = Array(e4.length), n22 = 0, r2 = () => {
      ++n22 == e4.length && Ii(s99, t5, i9.filter((o4) => o4 != null).join(s99.state.lineBreak), false);
    };
    for (let o4 = 0; o4 < e4.length; o4++) {
      let l11 = new FileReader();
      l11.onerror = r2, l11.onload = () => {
        /[\x00-\x08\x0e-\x1f]{2}/.test(l11.result) || (i9[o4] = l11.result), r2();
      }, l11.readAsText(e4[o4]);
    }
  } else Ii(s99, t5, t5.dataTransfer.getData("Text"), true);
};
E2.paste = (s99, t5) => {
  if (s99.state.readOnly) return t5.preventDefault();
  s99.observer.flush();
  let e4 = Ks ? null : t5.clipboardData;
  e4 ? (js(s99, e4.getData("text/plain")), t5.preventDefault()) : jn(s99);
};
function Yn(s99, t5) {
  let e4 = s99.dom.parentNode;
  if (!e4) return;
  let i9 = e4.appendChild(document.createElement("textarea"));
  i9.style.cssText = "position: fixed; left: -10000px; top: 10px", i9.value = t5, i9.focus(), i9.selectionEnd = t5.length, i9.selectionStart = 0, setTimeout(() => {
    i9.remove(), s99.focus();
  }, 50);
}
function Un(s99) {
  let t5 = [], e4 = [], i9 = false;
  for (let n22 of s99.selection.ranges) n22.empty || (t5.push(s99.sliceDoc(n22.from, n22.to)), e4.push(n22));
  if (!t5.length) {
    let n22 = -1;
    for (let { from: r2 } of s99.selection.ranges) {
      let o4 = s99.doc.lineAt(r2);
      o4.number > n22 && (t5.push(o4.text), e4.push({
        from: o4.from,
        to: Math.min(s99.doc.length, o4.to + 1)
      })), n22 = o4.number;
    }
    i9 = true;
  }
  return {
    text: t5.join(s99.lineBreak),
    ranges: e4,
    linewise: i9
  };
}
var _e2 = null;
E2.copy = E2.cut = (s99, t5) => {
  let { text: e4, ranges: i9, linewise: n22 } = Un(s99.state);
  if (!e4 && !n22) return;
  _e2 = n22 ? e4 : null;
  let r2 = Ks ? null : t5.clipboardData;
  r2 ? (t5.preventDefault(), r2.clearData(), r2.setData("text/plain", e4)) : Yn(s99, e4), t5.type == "cut" && !s99.state.readOnly && s99.dispatch({
    changes: i9,
    scrollIntoView: true,
    userEvent: "delete.cut"
  });
};
function _s(s99) {
  setTimeout(() => {
    s99.hasFocus != s99.inputState.notifiedFocused && s99.update([]);
  }, 10);
}
E2.focus = _s;
E2.blur = (s99) => {
  s99.observer.clearSelectionRange(), _s(s99);
};
function Ys(s99, t5) {
  if (s99.docView.compositionDeco.size) {
    s99.inputState.rapidCompositionStart = t5;
    try {
      s99.update([]);
    } finally {
      s99.inputState.rapidCompositionStart = false;
    }
  }
}
E2.compositionstart = E2.compositionupdate = (s99) => {
  s99.inputState.compositionFirstChange == null && (s99.inputState.compositionFirstChange = true), s99.inputState.composing < 0 && (s99.inputState.composing = 0, s99.docView.compositionDeco.size && (s99.observer.flush(), Ys(s99, true)));
};
E2.compositionend = (s99) => {
  s99.inputState.composing = -1, s99.inputState.compositionEndedAt = Date.now(), s99.inputState.compositionFirstChange = null, setTimeout(() => {
    s99.inputState.composing < 0 && Ys(s99, false);
  }, 50);
};
E2.contextmenu = (s99) => {
  s99.inputState.lastContextMenu = Date.now();
};
E2.beforeinput = (s99, t5) => {
  var e4;
  let i9;
  if (g2.chrome && g2.android && (i9 = Is.find((n22) => n22.inputType == t5.inputType)) && (s99.observer.delayAndroidKey(i9.key, i9.keyCode), i9.key == "Backspace" || i9.key == "Delete")) {
    let n22 = ((e4 = globalThis.visualViewport) === null || e4 === void 0 ? void 0 : e4.height) || 0;
    setTimeout(() => {
      var r2;
      (((r2 = globalThis.visualViewport) === null || r2 === void 0 ? void 0 : r2.height) || 0) > n22 + 10 && s99.hasFocus && (s99.contentDOM.blur(), s99.focus());
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
  heightForGap(t5, e4) {
    let i9 = this.doc.lineAt(e4).number - this.doc.lineAt(t5).number + 1;
    return this.lineWrapping && (i9 += Math.ceil((e4 - t5 - i9 * this.lineLength * 0.5) / this.lineLength)), this.lineHeight * i9;
  }
  heightForLine(t5) {
    return this.lineWrapping ? (1 + Math.max(0, Math.ceil((t5 - this.lineLength) / (this.lineLength - 5)))) * this.lineHeight : this.lineHeight;
  }
  setDoc(t5) {
    return this.doc = t5, this;
  }
  mustRefreshForWrapping(t5) {
    return qi.indexOf(t5) > -1 != this.lineWrapping;
  }
  mustRefreshForHeights(t5) {
    let e4 = false;
    for (let i9 = 0; i9 < t5.length; i9++) {
      let n22 = t5[i9];
      n22 < 0 ? i9++ : this.heightSamples[Math.floor(n22 * 10)] || (e4 = true, this.heightSamples[Math.floor(n22 * 10)] = true);
    }
    return e4;
  }
  refresh(t5, e4, i9, n22, r2) {
    let o4 = qi.indexOf(t5) > -1, l11 = Math.round(e4) != Math.round(this.lineHeight) || this.lineWrapping != o4;
    if (this.lineWrapping = o4, this.lineHeight = e4, this.charWidth = i9, this.lineLength = n22, l11) {
      this.heightSamples = {};
      for (let h3 = 0; h3 < r2.length; h3++) {
        let a2 = r2[h3];
        a2 < 0 ? h3++ : this.heightSamples[Math.floor(a2 * 10)] = true;
      }
    }
    return l11;
  }
};
var he2 = class {
  constructor(t5, e4) {
    this.from = t5, this.heights = e4, this.index = 0;
  }
  get more() {
    return this.index < this.heights.length;
  }
};
var J2 = class s36 {
  constructor(t5, e4, i9, n22, r2) {
    this.from = t5, this.length = e4, this.top = i9, this.height = n22, this.type = r2;
  }
  get to() {
    return this.from + this.length;
  }
  get bottom() {
    return this.top + this.height;
  }
  join(t5) {
    let e4 = (Array.isArray(this.type) ? this.type : [
      this
    ]).concat(Array.isArray(t5.type) ? t5.type : [
      t5
    ]);
    return new s36(this.from, this.length + t5.length, this.top, this.height + t5.height, e4);
  }
};
var A = function(s99) {
  return s99[s99.ByPos = 0] = "ByPos", s99[s99.ByHeight = 1] = "ByHeight", s99[s99.ByPosNoHeight = 2] = "ByPosNoHeight", s99;
}(A || (A = {}));
var jt = 1e-3;
var W2 = class s37 {
  constructor(t5, e4, i9 = 2) {
    this.length = t5, this.height = e4, this.flags = i9;
  }
  get outdated() {
    return (this.flags & 2) > 0;
  }
  set outdated(t5) {
    this.flags = (t5 ? 2 : 0) | this.flags & -3;
  }
  setHeight(t5, e4) {
    this.height != e4 && (Math.abs(this.height - e4) > jt && (t5.heightChanged = true), this.height = e4);
  }
  replace(t5, e4, i9) {
    return s37.of(i9);
  }
  decomposeLeft(t5, e4) {
    e4.push(this);
  }
  decomposeRight(t5, e4) {
    e4.push(this);
  }
  applyChanges(t5, e4, i9, n22) {
    let r2 = this;
    for (let o4 = n22.length - 1; o4 >= 0; o4--) {
      let { fromA: l11, toA: h3, fromB: a2, toB: c4 } = n22[o4], f2 = r2.lineAt(l11, A.ByPosNoHeight, e4, 0, 0), u5 = f2.to >= h3 ? f2 : r2.lineAt(h3, A.ByPosNoHeight, e4, 0, 0);
      for (c4 += u5.to - h3, h3 = u5.to; o4 > 0 && f2.from <= n22[o4 - 1].toA; ) l11 = n22[o4 - 1].fromA, a2 = n22[o4 - 1].fromB, o4--, l11 < f2.from && (f2 = r2.lineAt(l11, A.ByPosNoHeight, e4, 0, 0));
      a2 += f2.from - l11, l11 = f2.from;
      let d5 = Ue2.build(i9, t5, a2, c4);
      r2 = r2.replace(l11, h3, d5);
    }
    return r2.updateHeight(i9, 0);
  }
  static empty() {
    return new z2(0, 0);
  }
  static of(t5) {
    if (t5.length == 1) return t5[0];
    let e4 = 0, i9 = t5.length, n22 = 0, r2 = 0;
    for (; ; ) if (e4 == i9) if (n22 > r2 * 2) {
      let l11 = t5[e4 - 1];
      l11.break ? t5.splice(--e4, 1, l11.left, null, l11.right) : t5.splice(--e4, 1, l11.left, l11.right), i9 += 1 + l11.break, n22 -= l11.size;
    } else if (r2 > n22 * 2) {
      let l11 = t5[i9];
      l11.break ? t5.splice(i9, 1, l11.left, null, l11.right) : t5.splice(i9, 1, l11.left, l11.right), i9 += 2 + l11.break, r2 -= l11.size;
    } else break;
    else if (n22 < r2) {
      let l11 = t5[e4++];
      l11 && (n22 += l11.size);
    } else {
      let l11 = t5[--i9];
      l11 && (r2 += l11.size);
    }
    let o4 = 0;
    return t5[e4 - 1] == null ? (o4 = 1, e4--) : t5[e4] == null && (o4 = 1, i9++), new Ye2(s37.of(t5.slice(0, e4)), o4, s37.of(t5.slice(i9)));
  }
};
W2.prototype.size = 1;
var ae2 = class extends W2 {
  constructor(t5, e4, i9) {
    super(t5, e4), this.type = i9;
  }
  blockAt(t5, e4, i9, n22) {
    return new J2(n22, this.length, i9, this.height, this.type);
  }
  lineAt(t5, e4, i9, n22, r2) {
    return this.blockAt(0, i9, n22, r2);
  }
  forEachLine(t5, e4, i9, n22, r2, o4) {
    t5 <= r2 + this.length && e4 >= r2 && o4(this.blockAt(0, i9, n22, r2));
  }
  updateHeight(t5, e4 = 0, i9 = false, n22) {
    return n22 && n22.from <= e4 && n22.more && this.setHeight(t5, n22.heights[n22.index++]), this.outdated = false, this;
  }
  toString() {
    return `block(${this.length})`;
  }
};
var z2 = class s38 extends ae2 {
  constructor(t5, e4) {
    super(t5, e4, D2.Text), this.collapsed = 0, this.widgetHeight = 0;
  }
  replace(t5, e4, i9) {
    let n22 = i9[0];
    return i9.length == 1 && (n22 instanceof s38 || n22 instanceof tt2 && n22.flags & 4) && Math.abs(this.length - n22.length) < 10 ? (n22 instanceof tt2 ? n22 = new s38(n22.length, this.height) : n22.height = this.height, this.outdated || (n22.outdated = false), n22) : W2.of(i9);
  }
  updateHeight(t5, e4 = 0, i9 = false, n22) {
    return n22 && n22.from <= e4 && n22.more ? this.setHeight(t5, n22.heights[n22.index++]) : (i9 || this.outdated) && this.setHeight(t5, Math.max(this.widgetHeight, t5.heightForLine(this.length - this.collapsed))), this.outdated = false, this;
  }
  toString() {
    return `line(${this.length}${this.collapsed ? -this.collapsed : ""}${this.widgetHeight ? ":" + this.widgetHeight : ""})`;
  }
};
var tt2 = class s39 extends W2 {
  constructor(t5) {
    super(t5, 0);
  }
  lines(t5, e4) {
    let i9 = t5.lineAt(e4).number, n22 = t5.lineAt(e4 + this.length).number;
    return {
      firstLine: i9,
      lastLine: n22,
      lineHeight: this.height / (n22 - i9 + 1)
    };
  }
  blockAt(t5, e4, i9, n22) {
    let { firstLine: r2, lastLine: o4, lineHeight: l11 } = this.lines(e4, n22), h3 = Math.max(0, Math.min(o4 - r2, Math.floor((t5 - i9) / l11))), { from: a2, length: c4 } = e4.line(r2 + h3);
    return new J2(a2, c4, i9 + l11 * h3, l11, D2.Text);
  }
  lineAt(t5, e4, i9, n22, r2) {
    if (e4 == A.ByHeight) return this.blockAt(t5, i9, n22, r2);
    if (e4 == A.ByPosNoHeight) {
      let { from: f2, to: u5 } = i9.lineAt(t5);
      return new J2(f2, u5 - f2, 0, 0, D2.Text);
    }
    let { firstLine: o4, lineHeight: l11 } = this.lines(i9, r2), { from: h3, length: a2, number: c4 } = i9.lineAt(t5);
    return new J2(h3, a2, n22 + l11 * (c4 - o4), l11, D2.Text);
  }
  forEachLine(t5, e4, i9, n22, r2, o4) {
    let { firstLine: l11, lineHeight: h3 } = this.lines(i9, r2);
    for (let a2 = Math.max(t5, r2), c4 = Math.min(r2 + this.length, e4); a2 <= c4; ) {
      let f2 = i9.lineAt(a2);
      a2 == t5 && (n22 += h3 * (f2.number - l11)), o4(new J2(f2.from, f2.length, n22, h3, D2.Text)), n22 += h3, a2 = f2.to + 1;
    }
  }
  replace(t5, e4, i9) {
    let n22 = this.length - e4;
    if (n22 > 0) {
      let r2 = i9[i9.length - 1];
      r2 instanceof s39 ? i9[i9.length - 1] = new s39(r2.length + n22) : i9.push(null, new s39(n22 - 1));
    }
    if (t5 > 0) {
      let r2 = i9[0];
      r2 instanceof s39 ? i9[0] = new s39(t5 + r2.length) : i9.unshift(new s39(t5 - 1), null);
    }
    return W2.of(i9);
  }
  decomposeLeft(t5, e4) {
    e4.push(new s39(t5 - 1), null);
  }
  decomposeRight(t5, e4) {
    e4.push(null, new s39(this.length - t5 - 1));
  }
  updateHeight(t5, e4 = 0, i9 = false, n22) {
    let r2 = e4 + this.length;
    if (n22 && n22.from <= e4 + this.length && n22.more) {
      let o4 = [], l11 = Math.max(e4, n22.from), h3 = -1, a2 = t5.heightChanged;
      for (n22.from > e4 && o4.push(new s39(n22.from - e4 - 1).updateHeight(t5, e4)); l11 <= r2 && n22.more; ) {
        let f2 = t5.doc.lineAt(l11).length;
        o4.length && o4.push(null);
        let u5 = n22.heights[n22.index++];
        h3 == -1 ? h3 = u5 : Math.abs(u5 - h3) >= jt && (h3 = -2);
        let d5 = new z2(f2, u5);
        d5.outdated = false, o4.push(d5), l11 += f2 + 1;
      }
      l11 <= r2 && o4.push(null, new s39(r2 - l11).updateHeight(t5, l11));
      let c4 = W2.of(o4);
      return t5.heightChanged = a2 || h3 < 0 || Math.abs(c4.height - this.height) >= jt || Math.abs(h3 - this.lines(t5.doc, e4).lineHeight) >= jt, c4;
    } else (i9 || this.outdated) && (this.setHeight(t5, t5.heightForGap(e4, e4 + this.length)), this.outdated = false);
    return this;
  }
  toString() {
    return `gap(${this.length})`;
  }
};
var Ye2 = class extends W2 {
  constructor(t5, e4, i9) {
    super(t5.length + e4 + i9.length, t5.height + i9.height, e4 | (t5.outdated || i9.outdated ? 2 : 0)), this.left = t5, this.right = i9, this.size = t5.size + i9.size;
  }
  get break() {
    return this.flags & 1;
  }
  blockAt(t5, e4, i9, n22) {
    let r2 = i9 + this.left.height;
    return t5 < r2 ? this.left.blockAt(t5, e4, i9, n22) : this.right.blockAt(t5, e4, r2, n22 + this.left.length + this.break);
  }
  lineAt(t5, e4, i9, n22, r2) {
    let o4 = n22 + this.left.height, l11 = r2 + this.left.length + this.break, h3 = e4 == A.ByHeight ? t5 < o4 : t5 < l11, a2 = h3 ? this.left.lineAt(t5, e4, i9, n22, r2) : this.right.lineAt(t5, e4, i9, o4, l11);
    if (this.break || (h3 ? a2.to < l11 : a2.from > l11)) return a2;
    let c4 = e4 == A.ByPosNoHeight ? A.ByPosNoHeight : A.ByPos;
    return h3 ? a2.join(this.right.lineAt(l11, c4, i9, o4, l11)) : this.left.lineAt(l11, c4, i9, n22, r2).join(a2);
  }
  forEachLine(t5, e4, i9, n22, r2, o4) {
    let l11 = n22 + this.left.height, h3 = r2 + this.left.length + this.break;
    if (this.break) t5 < h3 && this.left.forEachLine(t5, e4, i9, n22, r2, o4), e4 >= h3 && this.right.forEachLine(t5, e4, i9, l11, h3, o4);
    else {
      let a2 = this.lineAt(h3, A.ByPos, i9, n22, r2);
      t5 < a2.from && this.left.forEachLine(t5, a2.from - 1, i9, n22, r2, o4), a2.to >= t5 && a2.from <= e4 && o4(a2), e4 > a2.to && this.right.forEachLine(a2.to + 1, e4, i9, l11, h3, o4);
    }
  }
  replace(t5, e4, i9) {
    let n22 = this.left.length + this.break;
    if (e4 < n22) return this.balanced(this.left.replace(t5, e4, i9), this.right);
    if (t5 > this.left.length) return this.balanced(this.left, this.right.replace(t5 - n22, e4 - n22, i9));
    let r2 = [];
    t5 > 0 && this.decomposeLeft(t5, r2);
    let o4 = r2.length;
    for (let l11 of i9) r2.push(l11);
    if (t5 > 0 && Ki(r2, o4 - 1), e4 < this.length) {
      let l11 = r2.length;
      this.decomposeRight(e4, r2), Ki(r2, l11);
    }
    return W2.of(r2);
  }
  decomposeLeft(t5, e4) {
    let i9 = this.left.length;
    if (t5 <= i9) return this.left.decomposeLeft(t5, e4);
    e4.push(this.left), this.break && (i9++, t5 >= i9 && e4.push(null)), t5 > i9 && this.right.decomposeLeft(t5 - i9, e4);
  }
  decomposeRight(t5, e4) {
    let i9 = this.left.length, n22 = i9 + this.break;
    if (t5 >= n22) return this.right.decomposeRight(t5 - n22, e4);
    t5 < i9 && this.left.decomposeRight(t5, e4), this.break && t5 < n22 && e4.push(null), e4.push(this.right);
  }
  balanced(t5, e4) {
    return t5.size > 2 * e4.size || e4.size > 2 * t5.size ? W2.of(this.break ? [
      t5,
      null,
      e4
    ] : [
      t5,
      e4
    ]) : (this.left = t5, this.right = e4, this.height = t5.height + e4.height, this.outdated = t5.outdated || e4.outdated, this.size = t5.size + e4.size, this.length = t5.length + this.break + e4.length, this);
  }
  updateHeight(t5, e4 = 0, i9 = false, n22) {
    let { left: r2, right: o4 } = this, l11 = e4 + r2.length + this.break, h3 = null;
    return n22 && n22.from <= e4 + r2.length && n22.more ? h3 = r2 = r2.updateHeight(t5, e4, i9, n22) : r2.updateHeight(t5, e4, i9), n22 && n22.from <= l11 + o4.length && n22.more ? h3 = o4 = o4.updateHeight(t5, l11, i9, n22) : o4.updateHeight(t5, l11, i9), h3 ? this.balanced(r2, o4) : (this.height = this.left.height + this.right.height, this.outdated = false, this);
  }
  toString() {
    return this.left + (this.break ? " " : "-") + this.right;
  }
};
function Ki(s99, t5) {
  let e4, i9;
  s99[t5] == null && (e4 = s99[t5 - 1]) instanceof tt2 && (i9 = s99[t5 + 1]) instanceof tt2 && s99.splice(t5 - 1, 3, new tt2(e4.length + 1 + i9.length));
}
var Xn = 5;
var Ue2 = class s40 {
  constructor(t5, e4) {
    this.pos = t5, this.oracle = e4, this.nodes = [], this.lineStart = -1, this.lineEnd = -1, this.covering = null, this.writtenTo = t5;
  }
  get isCovered() {
    return this.covering && this.nodes[this.nodes.length - 1] == this.covering;
  }
  span(t5, e4) {
    if (this.lineStart > -1) {
      let i9 = Math.min(e4, this.lineEnd), n22 = this.nodes[this.nodes.length - 1];
      n22 instanceof z2 ? n22.length += i9 - this.pos : (i9 > this.pos || !this.isCovered) && this.nodes.push(new z2(i9 - this.pos, -1)), this.writtenTo = i9, e4 > i9 && (this.nodes.push(null), this.writtenTo++, this.lineStart = -1);
    }
    this.pos = e4;
  }
  point(t5, e4, i9) {
    if (t5 < e4 || i9.heightRelevant) {
      let n22 = i9.widget ? i9.widget.estimatedHeight : 0;
      n22 < 0 && (n22 = this.oracle.lineHeight);
      let r2 = e4 - t5;
      i9.block ? this.addBlock(new ae2(r2, n22, i9.type)) : (r2 || n22 >= Xn) && this.addLineDeco(n22, r2);
    } else e4 > t5 && this.span(t5, e4);
    this.lineEnd > -1 && this.lineEnd < this.pos && (this.lineEnd = this.oracle.doc.lineAt(this.pos).to);
  }
  enterLine() {
    if (this.lineStart > -1) return;
    let { from: t5, to: e4 } = this.oracle.doc.lineAt(this.pos);
    this.lineStart = t5, this.lineEnd = e4, this.writtenTo < t5 && ((this.writtenTo < t5 - 1 || this.nodes[this.nodes.length - 1] == null) && this.nodes.push(this.blankContent(this.writtenTo, t5 - 1)), this.nodes.push(null)), this.pos > t5 && this.nodes.push(new z2(this.pos - t5, -1)), this.writtenTo = this.pos;
  }
  blankContent(t5, e4) {
    let i9 = new tt2(e4 - t5);
    return this.oracle.doc.lineAt(t5).to == e4 && (i9.flags |= 4), i9;
  }
  ensureLine() {
    this.enterLine();
    let t5 = this.nodes.length ? this.nodes[this.nodes.length - 1] : null;
    if (t5 instanceof z2) return t5;
    let e4 = new z2(0, -1);
    return this.nodes.push(e4), e4;
  }
  addBlock(t5) {
    this.enterLine(), t5.type == D2.WidgetAfter && !this.isCovered && this.ensureLine(), this.nodes.push(t5), this.writtenTo = this.pos = this.pos + t5.length, t5.type != D2.WidgetBefore && (this.covering = t5);
  }
  addLineDeco(t5, e4) {
    let i9 = this.ensureLine();
    i9.length += e4, i9.collapsed += e4, i9.widgetHeight = Math.max(i9.widgetHeight, t5), this.writtenTo = this.pos = this.pos + e4;
  }
  finish(t5) {
    let e4 = this.nodes.length == 0 ? null : this.nodes[this.nodes.length - 1];
    this.lineStart > -1 && !(e4 instanceof z2) && !this.isCovered ? this.nodes.push(new z2(0, -1)) : (this.writtenTo < this.pos || e4 == null) && this.nodes.push(this.blankContent(this.writtenTo, this.pos));
    let i9 = t5;
    for (let n22 of this.nodes) n22 instanceof z2 && n22.updateHeight(this.oracle, i9), i9 += n22 ? n22.length : 1;
    return this.nodes;
  }
  static build(t5, e4, i9, n22) {
    let r2 = new s40(i9, t5);
    return O.spans(e4, i9, n22, r2, 0), r2.finish(i9);
  }
};
function Jn(s99, t5, e4) {
  let i9 = new Xe2();
  return O.compare(s99, t5, e4, i9, 0), i9.changes;
}
var Xe2 = class {
  constructor() {
    this.changes = [];
  }
  compareRange() {
  }
  comparePoint(t5, e4, i9, n22) {
    (t5 < e4 || i9 && i9.heightRelevant || n22 && n22.heightRelevant) && Ne2(t5, e4, this.changes, 5);
  }
};
function Zn(s99, t5) {
  let e4 = s99.getBoundingClientRect(), i9 = Math.max(0, e4.left), n22 = Math.min(innerWidth, e4.right), r2 = Math.max(0, e4.top), o4 = Math.min(innerHeight, e4.bottom), l11 = s99.ownerDocument.body;
  for (let h3 = s99.parentNode; h3 && h3 != l11; ) if (h3.nodeType == 1) {
    let a2 = h3, c4 = globalThis.getComputedStyle(a2);
    if ((a2.scrollHeight > a2.clientHeight || a2.scrollWidth > a2.clientWidth) && c4.overflow != "visible") {
      let f2 = a2.getBoundingClientRect();
      i9 = Math.max(i9, f2.left), n22 = Math.min(n22, f2.right), r2 = Math.max(r2, f2.top), o4 = Math.min(o4, f2.bottom);
    }
    h3 = c4.position == "absolute" || c4.position == "fixed" ? a2.offsetParent : a2.parentNode;
  } else if (h3.nodeType == 11) h3 = h3.host;
  else break;
  return {
    left: i9 - e4.left,
    right: Math.max(i9, n22) - e4.left,
    top: r2 - (e4.top + t5),
    bottom: Math.max(r2, o4) - (e4.top + t5)
  };
}
function Qn(s99, t5) {
  let e4 = s99.getBoundingClientRect();
  return {
    left: 0,
    right: e4.right - e4.left,
    top: t5,
    bottom: e4.bottom - (e4.top + t5)
  };
}
var kt = class {
  constructor(t5, e4, i9) {
    this.from = t5, this.to = e4, this.size = i9;
  }
  static same(t5, e4) {
    if (t5.length != e4.length) return false;
    for (let i9 = 0; i9 < t5.length; i9++) {
      let n22 = t5[i9], r2 = e4[i9];
      if (n22.from != r2.from || n22.to != r2.to || n22.size != r2.size) return false;
    }
    return true;
  }
  draw(t5) {
    return C2.replace({
      widget: new Je2(this.size, t5)
    }).range(this.from, this.to);
  }
};
var Je2 = class extends K2 {
  constructor(t5, e4) {
    super(), this.size = t5, this.vertical = e4;
  }
  eq(t5) {
    return t5.size == this.size && t5.vertical == this.vertical;
  }
  toDOM() {
    let t5 = document.createElement("div");
    return this.vertical ? t5.style.height = this.size + "px" : (t5.style.width = this.size + "px", t5.style.height = "2px", t5.style.display = "inline-block"), t5;
  }
  get estimatedHeight() {
    return this.vertical ? this.size : -1;
  }
};
var ce2 = class {
  constructor(t5) {
    this.state = t5, this.pixelViewport = {
      left: 0,
      right: globalThis.innerWidth,
      top: 0,
      bottom: 0
    }, this.inView = true, this.paddingTop = 0, this.paddingBottom = 0, this.contentDOMWidth = 0, this.contentDOMHeight = 0, this.editorHeight = 0, this.editorWidth = 0, this.heightOracle = new le(), this.scaler = $i, this.scrollTarget = null, this.printing = false, this.mustMeasureContent = true, this.defaultTextDirection = O2.RTL, this.visibleRanges = [], this.mustEnforceCursorAssoc = false, this.stateDeco = t5.facet(Ht).filter((e4) => typeof e4 != "function"), this.heightMap = W2.empty().applyChanges(this.stateDeco, m.empty, this.heightOracle.setDoc(t5.doc), [
      new it2(0, 0, 0, t5.doc.length)
    ]), this.viewport = this.getViewport(0, null), this.updateViewportLines(), this.updateForViewport(), this.lineGaps = this.ensureLineGaps([]), this.lineGapDeco = C2.set(this.lineGaps.map((e4) => e4.draw(false))), this.computeVisibleRanges();
  }
  updateForViewport() {
    let t5 = [
      this.viewport
    ], { main: e4 } = this.state.selection;
    for (let i9 = 0; i9 <= 1; i9++) {
      let n22 = i9 ? e4.head : e4.anchor;
      if (!t5.some(({ from: r2, to: o4 }) => n22 >= r2 && n22 <= o4)) {
        let { from: r2, to: o4 } = this.lineBlockAt(n22);
        t5.push(new at2(r2, o4));
      }
    }
    this.viewports = t5.sort((i9, n22) => i9.from - n22.from), this.scaler = this.heightMap.height <= 7e6 ? $i : new Ze2(this.heightOracle.doc, this.heightMap, this.viewports);
  }
  updateViewportLines() {
    this.viewportLines = [], this.heightMap.forEachLine(this.viewport.from, this.viewport.to, this.state.doc, 0, 0, (t5) => {
      this.viewportLines.push(this.scaler.scale == 1 ? t5 : wt(t5, this.scaler));
    });
  }
  update(t5, e4 = null) {
    this.state = t5.state;
    let i9 = this.stateDeco;
    this.stateDeco = this.state.facet(Ht).filter((a2) => typeof a2 != "function");
    let n22 = t5.changedRanges, r2 = it2.extendWithRanges(n22, Jn(i9, this.stateDeco, t5 ? t5.changes : P.empty(this.state.doc.length))), o4 = this.heightMap.height;
    this.heightMap = this.heightMap.applyChanges(this.stateDeco, t5.startState.doc, this.heightOracle.setDoc(this.state.doc), r2), this.heightMap.height != o4 && (t5.flags |= 2);
    let l11 = r2.length ? this.mapViewport(this.viewport, t5.changes) : this.viewport;
    (e4 && (e4.range.head < l11.from || e4.range.head > l11.to) || !this.viewportIsAppropriate(l11)) && (l11 = this.getViewport(0, e4));
    let h3 = !t5.changes.empty || t5.flags & 2 || l11.from != this.viewport.from || l11.to != this.viewport.to;
    this.viewport = l11, this.updateForViewport(), h3 && this.updateViewportLines(), (this.lineGaps.length || this.viewport.to - this.viewport.from > 4e3) && this.updateLineGaps(this.ensureLineGaps(this.mapLineGaps(this.lineGaps, t5.changes))), t5.flags |= this.computeVisibleRanges(), e4 && (this.scrollTarget = e4), !this.mustEnforceCursorAssoc && t5.selectionSet && t5.view.lineWrapping && t5.state.selection.main.empty && t5.state.selection.main.assoc && (this.mustEnforceCursorAssoc = true);
  }
  measure(t5) {
    let e4 = t5.contentDOM, i9 = globalThis.getComputedStyle(e4), n22 = this.heightOracle, r2 = i9.whiteSpace;
    this.defaultTextDirection = i9.direction == "rtl" ? O2.RTL : O2.LTR;
    let o4 = this.heightOracle.mustRefreshForWrapping(r2), l11 = o4 || this.mustMeasureContent || this.contentDOMHeight != e4.clientHeight;
    this.contentDOMHeight = e4.clientHeight, this.mustMeasureContent = false;
    let h3 = 0, a2 = 0, c4 = parseInt(i9.paddingTop) || 0, f2 = parseInt(i9.paddingBottom) || 0;
    (this.paddingTop != c4 || this.paddingBottom != f2) && (this.paddingTop = c4, this.paddingBottom = f2, h3 |= 10), this.editorWidth != t5.scrollDOM.clientWidth && (n22.lineWrapping && (l11 = true), this.editorWidth = t5.scrollDOM.clientWidth, h3 |= 8);
    let u5 = (this.printing ? Qn : Zn)(e4, this.paddingTop), d5 = u5.top - this.pixelViewport.top, p5 = u5.bottom - this.pixelViewport.bottom;
    this.pixelViewport = u5;
    let m9 = this.pixelViewport.bottom > this.pixelViewport.top && this.pixelViewport.right > this.pixelViewport.left;
    if (m9 != this.inView && (this.inView = m9, m9 && (l11 = true)), !this.inView) return 0;
    let b9 = e4.clientWidth;
    if ((this.contentDOMWidth != b9 || this.editorHeight != t5.scrollDOM.clientHeight) && (this.contentDOMWidth = b9, this.editorHeight = t5.scrollDOM.clientHeight, h3 |= 8), l11) {
      let k13 = t5.docView.measureVisibleLineHeights(this.viewport);
      if (n22.mustRefreshForHeights(k13) && (o4 = true), o4 || n22.lineWrapping && Math.abs(b9 - this.contentDOMWidth) > n22.charWidth) {
        let { lineHeight: v8, charWidth: w11 } = t5.docView.measureTextSize();
        o4 = n22.refresh(r2, v8, w11, b9 / w11, k13), o4 && (t5.docView.minWidth = 0, h3 |= 8);
      }
      d5 > 0 && p5 > 0 ? a2 = Math.max(d5, p5) : d5 < 0 && p5 < 0 && (a2 = Math.min(d5, p5)), n22.heightChanged = false;
      for (let v8 of this.viewports) {
        let w11 = v8.from == this.viewport.from ? k13 : t5.docView.measureVisibleLineHeights(v8);
        this.heightMap = this.heightMap.updateHeight(n22, 0, o4, new he2(v8.from, w11));
      }
      n22.heightChanged && (h3 |= 2);
    }
    let y10 = !this.viewportIsAppropriate(this.viewport, a2) || this.scrollTarget && (this.scrollTarget.range.head < this.viewport.from || this.scrollTarget.range.head > this.viewport.to);
    return y10 && (this.viewport = this.getViewport(a2, this.scrollTarget)), this.updateForViewport(), (h3 & 2 || y10) && this.updateViewportLines(), (this.lineGaps.length || this.viewport.to - this.viewport.from > 4e3) && this.updateLineGaps(this.ensureLineGaps(o4 ? [] : this.lineGaps)), h3 |= this.computeVisibleRanges(), this.mustEnforceCursorAssoc && (this.mustEnforceCursorAssoc = false, t5.docView.enforceCursorAssoc()), h3;
  }
  get visibleTop() {
    return this.scaler.fromDOM(this.pixelViewport.top);
  }
  get visibleBottom() {
    return this.scaler.fromDOM(this.pixelViewport.bottom);
  }
  getViewport(t5, e4) {
    let i9 = 0.5 - Math.max(-0.5, Math.min(0.5, t5 / 1e3 / 2)), n22 = this.heightMap, r2 = this.state.doc, { visibleTop: o4, visibleBottom: l11 } = this, h3 = new at2(n22.lineAt(o4 - i9 * 1e3, A.ByHeight, r2, 0, 0).from, n22.lineAt(l11 + (1 - i9) * 1e3, A.ByHeight, r2, 0, 0).to);
    if (e4) {
      let { head: a2 } = e4.range;
      if (a2 < h3.from || a2 > h3.to) {
        let c4 = Math.min(this.editorHeight, this.pixelViewport.bottom - this.pixelViewport.top), f2 = n22.lineAt(a2, A.ByPos, r2, 0, 0), u5;
        e4.y == "center" ? u5 = (f2.top + f2.bottom) / 2 - c4 / 2 : e4.y == "start" || e4.y == "nearest" && a2 < h3.from ? u5 = f2.top : u5 = f2.bottom - c4, h3 = new at2(n22.lineAt(u5 - 1e3 / 2, A.ByHeight, r2, 0, 0).from, n22.lineAt(u5 + c4 + 1e3 / 2, A.ByHeight, r2, 0, 0).to);
      }
    }
    return h3;
  }
  mapViewport(t5, e4) {
    let i9 = e4.mapPos(t5.from, -1), n22 = e4.mapPos(t5.to, 1);
    return new at2(this.heightMap.lineAt(i9, A.ByPos, this.state.doc, 0, 0).from, this.heightMap.lineAt(n22, A.ByPos, this.state.doc, 0, 0).to);
  }
  viewportIsAppropriate({ from: t5, to: e4 }, i9 = 0) {
    if (!this.inView) return true;
    let { top: n22 } = this.heightMap.lineAt(t5, A.ByPos, this.state.doc, 0, 0), { bottom: r2 } = this.heightMap.lineAt(e4, A.ByPos, this.state.doc, 0, 0), { visibleTop: o4, visibleBottom: l11 } = this;
    return (t5 == 0 || n22 <= o4 - Math.max(10, Math.min(-i9, 250))) && (e4 == this.state.doc.length || r2 >= l11 + Math.max(10, Math.min(i9, 250))) && n22 > o4 - 2 * 1e3 && r2 < l11 + 2 * 1e3;
  }
  mapLineGaps(t5, e4) {
    if (!t5.length || e4.empty) return t5;
    let i9 = [];
    for (let n22 of t5) e4.touchesRange(n22.from, n22.to) || i9.push(new kt(e4.mapPos(n22.from), e4.mapPos(n22.to), n22.size));
    return i9;
  }
  ensureLineGaps(t5) {
    let e4 = [];
    if (this.defaultTextDirection != O2.LTR) return e4;
    for (let i9 of this.viewportLines) {
      if (i9.length < 4e3) continue;
      let n22 = tr(i9.from, i9.to, this.stateDeco);
      if (n22.total < 4e3) continue;
      let r2, o4;
      if (this.heightOracle.lineWrapping) {
        let a2 = 2e3 / this.heightOracle.lineLength * this.heightOracle.lineHeight;
        r2 = qt(n22, (this.visibleTop - i9.top - a2) / i9.height), o4 = qt(n22, (this.visibleBottom - i9.top + a2) / i9.height);
      } else {
        let a2 = n22.total * this.heightOracle.charWidth, c4 = 2e3 * this.heightOracle.charWidth;
        r2 = qt(n22, (this.pixelViewport.left - c4) / a2), o4 = qt(n22, (this.pixelViewport.right + c4) / a2);
      }
      let l11 = [];
      r2 > i9.from && l11.push({
        from: i9.from,
        to: r2
      }), o4 < i9.to && l11.push({
        from: o4,
        to: i9.to
      });
      let h3 = this.state.selection.main;
      h3.from >= i9.from && h3.from <= i9.to && Gi(l11, h3.from - 10, h3.from + 10), !h3.empty && h3.to >= i9.from && h3.to <= i9.to && Gi(l11, h3.to - 10, h3.to + 10);
      for (let { from: a2, to: c4 } of l11) c4 - a2 > 1e3 && e4.push(er(t5, (f2) => f2.from >= i9.from && f2.to <= i9.to && Math.abs(f2.from - a2) < 1e3 && Math.abs(f2.to - c4) < 1e3) || new kt(a2, c4, this.gapSize(i9, a2, c4, n22)));
    }
    return e4;
  }
  gapSize(t5, e4, i9, n22) {
    let r2 = ji(n22, i9) - ji(n22, e4);
    return this.heightOracle.lineWrapping ? t5.height * r2 : n22.total * this.heightOracle.charWidth * r2;
  }
  updateLineGaps(t5) {
    kt.same(t5, this.lineGaps) || (this.lineGaps = t5, this.lineGapDeco = C2.set(t5.map((e4) => e4.draw(this.heightOracle.lineWrapping))));
  }
  computeVisibleRanges() {
    let t5 = this.stateDeco;
    this.lineGaps.length && (t5 = t5.concat(this.lineGapDeco));
    let e4 = [];
    O.spans(t5, this.viewport.from, this.viewport.to, {
      span(n22, r2) {
        e4.push({
          from: n22,
          to: r2
        });
      },
      point() {
      }
    }, 20);
    let i9 = e4.length != this.visibleRanges.length || this.visibleRanges.some((n22, r2) => n22.from != e4[r2].from || n22.to != e4[r2].to);
    return this.visibleRanges = e4, i9 ? 4 : 0;
  }
  lineBlockAt(t5) {
    return t5 >= this.viewport.from && t5 <= this.viewport.to && this.viewportLines.find((e4) => e4.from <= t5 && e4.to >= t5) || wt(this.heightMap.lineAt(t5, A.ByPos, this.state.doc, 0, 0), this.scaler);
  }
  lineBlockAtHeight(t5) {
    return wt(this.heightMap.lineAt(this.scaler.fromDOM(t5), A.ByHeight, this.state.doc, 0, 0), this.scaler);
  }
  elementAtHeight(t5) {
    return wt(this.heightMap.blockAt(this.scaler.fromDOM(t5), this.state.doc, 0, 0), this.scaler);
  }
  get docHeight() {
    return this.scaler.toDOM(this.heightMap.height);
  }
  get contentHeight() {
    return this.docHeight + this.paddingTop + this.paddingBottom;
  }
};
var at2 = class {
  constructor(t5, e4) {
    this.from = t5, this.to = e4;
  }
};
function tr(s99, t5, e4) {
  let i9 = [], n22 = s99, r2 = 0;
  return O.spans(e4, s99, t5, {
    span() {
    },
    point(o4, l11) {
      o4 > n22 && (i9.push({
        from: n22,
        to: o4
      }), r2 += o4 - n22), n22 = l11;
    }
  }, 20), n22 < t5 && (i9.push({
    from: n22,
    to: t5
  }), r2 += t5 - n22), {
    total: r2,
    ranges: i9
  };
}
function qt({ total: s99, ranges: t5 }, e4) {
  if (e4 <= 0) return t5[0].from;
  if (e4 >= 1) return t5[t5.length - 1].to;
  let i9 = Math.floor(s99 * e4);
  for (let n22 = 0; ; n22++) {
    let { from: r2, to: o4 } = t5[n22], l11 = o4 - r2;
    if (i9 <= l11) return r2 + i9;
    i9 -= l11;
  }
}
function ji(s99, t5) {
  let e4 = 0;
  for (let { from: i9, to: n22 } of s99.ranges) {
    if (t5 <= n22) {
      e4 += t5 - i9;
      break;
    }
    e4 += n22 - i9;
  }
  return e4 / s99.total;
}
function Gi(s99, t5, e4) {
  for (let i9 = 0; i9 < s99.length; i9++) {
    let n22 = s99[i9];
    if (n22.from < e4 && n22.to > t5) {
      let r2 = [];
      n22.from < t5 && r2.push({
        from: n22.from,
        to: t5
      }), n22.to > e4 && r2.push({
        from: e4,
        to: n22.to
      }), s99.splice(i9, 1, ...r2), i9 += r2.length - 1;
    }
  }
}
function er(s99, t5) {
  for (let e4 of s99) if (t5(e4)) return e4;
}
var $i = {
  toDOM(s99) {
    return s99;
  },
  fromDOM(s99) {
    return s99;
  },
  scale: 1
};
var Ze2 = class {
  constructor(t5, e4, i9) {
    let n22 = 0, r2 = 0, o4 = 0;
    this.viewports = i9.map(({ from: l11, to: h3 }) => {
      let a2 = e4.lineAt(l11, A.ByPos, t5, 0, 0).top, c4 = e4.lineAt(h3, A.ByPos, t5, 0, 0).bottom;
      return n22 += c4 - a2, {
        from: l11,
        to: h3,
        top: a2,
        bottom: c4,
        domTop: 0,
        domBottom: 0
      };
    }), this.scale = (7e6 - n22) / (e4.height - n22);
    for (let l11 of this.viewports) l11.domTop = o4 + (l11.top - r2) * this.scale, o4 = l11.domBottom = l11.domTop + (l11.bottom - l11.top), r2 = l11.bottom;
  }
  toDOM(t5) {
    for (let e4 = 0, i9 = 0, n22 = 0; ; e4++) {
      let r2 = e4 < this.viewports.length ? this.viewports[e4] : null;
      if (!r2 || t5 < r2.top) return n22 + (t5 - i9) * this.scale;
      if (t5 <= r2.bottom) return r2.domTop + (t5 - r2.top);
      i9 = r2.bottom, n22 = r2.domBottom;
    }
  }
  fromDOM(t5) {
    for (let e4 = 0, i9 = 0, n22 = 0; ; e4++) {
      let r2 = e4 < this.viewports.length ? this.viewports[e4] : null;
      if (!r2 || t5 < r2.domTop) return i9 + (t5 - n22) / this.scale;
      if (t5 <= r2.domBottom) return r2.top + (t5 - r2.domTop);
      i9 = r2.bottom, n22 = r2.domBottom;
    }
  }
};
function wt(s99, t5) {
  if (t5.scale == 1) return s99;
  let e4 = t5.toDOM(s99.top), i9 = t5.toDOM(s99.bottom);
  return new J2(s99.from, s99.length, e4, i9 - e4, Array.isArray(s99.type) ? s99.type.map((n22) => wt(n22, t5)) : s99.type);
}
var Kt = y.define({
  combine: (s99) => s99.join(" ")
});
var Qe2 = y.define({
  combine: (s99) => s99.indexOf(true) > -1
});
var ti = T2.newName();
var Us = T2.newName();
var Xs = T2.newName();
var Js = {
  "&light": "." + Us,
  "&dark": "." + Xs
};
function ei(s99, t5, e4) {
  return new T2(t5, {
    finish(i9) {
      return /&/.test(i9) ? i9.replace(/&\w*/, (n22) => {
        if (n22 == "&") return s99;
        if (!e4 || !e4[n22]) throw new RangeError(`Unsupported selector: ${n22}`);
        return e4[n22];
      }) : s99 + " " + i9;
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
  constructor(t5, e4, i9) {
    this.view = t5, this.onChange = e4, this.onScrollChanged = i9, this.active = false, this.selectionRange = new Oe2(), this.selectionChanged = false, this.delayedFlush = -1, this.resizeTimeout = -1, this.queue = [], this.delayedAndroidKey = null, this.scrollTargets = [], this.intersection = null, this.resize = null, this.intersecting = false, this.gapIntersection = null, this.gaps = [], this.parentCheck = -1, this.dom = t5.contentDOM, this.observer = new MutationObserver((n22) => {
      for (let r2 of n22) this.queue.push(r2);
      (g2.ie && g2.ie_version <= 11 || g2.ios && t5.composing) && n22.some((r2) => r2.type == "childList" && r2.removedNodes.length || r2.type == "characterData" && r2.oldValue.length > r2.target.nodeValue.length) ? this.flushSoon() : this.flush();
    }), xe2 && (this.onCharData = (n22) => {
      this.queue.push({
        target: n22.target,
        type: "characterData",
        oldValue: n22.prevValue
      }), this.flushSoon();
    }), this.onSelectionChange = this.onSelectionChange.bind(this), globalThis.addEventListener("resize", this.onResize = this.onResize.bind(this)), typeof ResizeObserver == "function" && (this.resize = new ResizeObserver(() => {
      this.view.docView.lastUpdate < Date.now() - 75 && this.onResize();
    }), this.resize.observe(t5.scrollDOM)), globalThis.addEventListener("beforeprint", this.onPrint = this.onPrint.bind(this)), this.start(), globalThis.addEventListener("scroll", this.onScroll = this.onScroll.bind(this)), typeof IntersectionObserver == "function" && (this.intersection = new IntersectionObserver((n22) => {
      this.parentCheck < 0 && (this.parentCheck = setTimeout(this.listenForScroll.bind(this), 1e3)), n22.length > 0 && n22[n22.length - 1].intersectionRatio > 0 != this.intersecting && (this.intersecting = !this.intersecting, this.intersecting != this.view.inView && this.onScrollChanged(document.createEvent("Event")));
    }, {}), this.intersection.observe(this.dom), this.gapIntersection = new IntersectionObserver((n22) => {
      n22.length > 0 && n22[n22.length - 1].intersectionRatio > 0 && this.onScrollChanged(document.createEvent("Event"));
    }, {})), this.listenForScroll(), this.readSelectionRange(), this.dom.ownerDocument.addEventListener("selectionchange", this.onSelectionChange);
  }
  onScroll(t5) {
    this.intersecting && this.flush(false), this.onScrollChanged(t5);
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
  updateGaps(t5) {
    if (this.gapIntersection && (t5.length != this.gaps.length || this.gaps.some((e4, i9) => e4 != t5[i9]))) {
      this.gapIntersection.disconnect();
      for (let e4 of t5) this.gapIntersection.observe(e4);
      this.gaps = t5;
    }
  }
  onSelectionChange(t5) {
    if (!this.readSelectionRange() || this.delayedAndroidKey) return;
    let { view: e4 } = this, i9 = this.selectionRange;
    if (e4.state.facet(Nt) ? e4.root.activeElement != this.dom : !De2(e4.dom, i9)) return;
    let n22 = i9.anchorNode && e4.docView.nearest(i9.anchorNode);
    n22 && n22.ignoreEvent(t5) || ((g2.ie && g2.ie_version <= 11 || g2.android && g2.chrome) && !e4.state.selection.main.empty && i9.focusNode && Ut(i9.focusNode, i9.focusOffset, i9.anchorNode, i9.anchorOffset) ? this.flushSoon() : this.flush(false));
  }
  readSelectionRange() {
    let { root: t5 } = this.view, e4 = Yt(t5), i9 = g2.safari && t5.nodeType == 11 && gn() == this.view.contentDOM && nr(this.view) || e4;
    return this.selectionRange.eq(i9) ? false : (this.selectionRange.setRange(i9), this.selectionChanged = true);
  }
  setSelectionRange(t5, e4) {
    this.selectionRange.set(t5.node, t5.offset, e4.node, e4.offset), this.selectionChanged = false;
  }
  clearSelectionRange() {
    this.selectionRange.set(null, 0, null, 0);
  }
  listenForScroll() {
    this.parentCheck = -1;
    let t5 = 0, e4 = null;
    for (let i9 = this.dom; i9; ) if (i9.nodeType == 1) !e4 && t5 < this.scrollTargets.length && this.scrollTargets[t5] == i9 ? t5++ : e4 || (e4 = this.scrollTargets.slice(0, t5)), e4 && e4.push(i9), i9 = i9.assignedSlot || i9.parentNode;
    else if (i9.nodeType == 11) i9 = i9.host;
    else break;
    if (t5 < this.scrollTargets.length && !e4 && (e4 = this.scrollTargets.slice(0, t5)), e4) {
      for (let i9 of this.scrollTargets) i9.removeEventListener("scroll", this.onScroll);
      for (let i9 of this.scrollTargets = e4) i9.addEventListener("scroll", this.onScroll);
    }
  }
  ignore(t5) {
    if (!this.active) return t5();
    try {
      return this.stop(), t5();
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
  delayAndroidKey(t5, e4) {
    this.delayedAndroidKey || requestAnimationFrame(() => {
      let i9 = this.delayedAndroidKey;
      this.delayedAndroidKey = null, this.delayedFlush = -1, this.flush() || Ct(this.view.contentDOM, i9.key, i9.keyCode);
    }), (!this.delayedAndroidKey || t5 == "Enter") && (this.delayedAndroidKey = {
      key: t5,
      keyCode: e4
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
    let t5 = this.queue;
    for (let r2 of this.observer.takeRecords()) t5.push(r2);
    t5.length && (this.queue = []);
    let e4 = -1, i9 = -1, n22 = false;
    for (let r2 of t5) {
      let o4 = this.readMutation(r2);
      o4 && (o4.typeOver && (n22 = true), e4 == -1 ? { from: e4, to: i9 } = o4 : (e4 = Math.min(o4.from, e4), i9 = Math.max(o4.to, i9)));
    }
    return {
      from: e4,
      to: i9,
      typeOver: n22
    };
  }
  flush(t5 = true) {
    if (this.delayedFlush >= 0 || this.delayedAndroidKey) return;
    t5 && this.readSelectionRange();
    let { from: e4, to: i9, typeOver: n22 } = this.processRecords(), r2 = this.selectionChanged && De2(this.dom, this.selectionRange);
    if (e4 < 0 && !r2) return;
    this.selectionChanged = false;
    let o4 = this.view.state, l11 = this.onChange(e4, i9, n22);
    return this.view.state == o4 && this.view.update([]), l11;
  }
  readMutation(t5) {
    let e4 = this.view.docView.nearest(t5.target);
    if (!e4 || e4.ignoreMutation(t5)) return null;
    if (e4.markDirty(t5.type == "attributes"), t5.type == "attributes" && (e4.dirty |= 4), t5.type == "childList") {
      let i9 = _i(e4, t5.previousSibling || t5.target.previousSibling, -1), n22 = _i(e4, t5.nextSibling || t5.target.nextSibling, 1);
      return {
        from: i9 ? e4.posAfter(i9) : e4.posAtStart,
        to: n22 ? e4.posBefore(n22) : e4.posAtEnd,
        typeOver: false
      };
    } else return t5.type == "characterData" ? {
      from: e4.posAtStart,
      to: e4.posAtEnd,
      typeOver: t5.target.nodeValue == t5.oldValue
    } : null;
  }
  destroy() {
    var t5, e4, i9;
    this.stop(), (t5 = this.intersection) === null || t5 === void 0 || t5.disconnect(), (e4 = this.gapIntersection) === null || e4 === void 0 || e4.disconnect(), (i9 = this.resize) === null || i9 === void 0 || i9.disconnect();
    for (let n22 of this.scrollTargets) n22.removeEventListener("scroll", this.onScroll);
    globalThis.removeEventListener("scroll", this.onScroll), globalThis.removeEventListener("resize", this.onResize), globalThis.removeEventListener("beforeprint", this.onPrint), this.dom.ownerDocument.removeEventListener("selectionchange", this.onSelectionChange), clearTimeout(this.parentCheck), clearTimeout(this.resizeTimeout);
  }
};
function _i(s99, t5, e4) {
  for (; t5; ) {
    let i9 = R2.get(t5);
    if (i9 && i9.parent == s99) return i9;
    let n22 = t5.parentNode;
    t5 = n22 != s99.dom ? n22 : e4 > 0 ? t5.nextSibling : t5.previousSibling;
  }
  return null;
}
function nr(s99) {
  let t5 = null;
  function e4(h3) {
    h3.preventDefault(), h3.stopImmediatePropagation(), t5 = h3.getTargetRanges()[0];
  }
  if (s99.contentDOM.addEventListener("beforeinput", e4, true), document.execCommand("indent"), s99.contentDOM.removeEventListener("beforeinput", e4, true), !t5) return null;
  let i9 = t5.startContainer, n22 = t5.startOffset, r2 = t5.endContainer, o4 = t5.endOffset, l11 = s99.docView.domAtPos(s99.state.selection.main.anchor);
  return Ut(l11.node, l11.offset, r2, o4) && ([i9, n22, r2, o4] = [
    r2,
    o4,
    i9,
    n22
  ]), {
    anchorNode: i9,
    anchorOffset: n22,
    focusNode: r2,
    focusOffset: o4
  };
}
function rr(s99, t5, e4, i9) {
  let n22, r2, o4 = s99.state.selection.main;
  if (t5 > -1) {
    let l11 = s99.docView.domBoundsAround(t5, e4, 0);
    if (!l11 || s99.state.readOnly) return false;
    let { from: h3, to: a2 } = l11, c4 = s99.docView.impreciseHead || s99.docView.impreciseAnchor ? [] : lr(s99), f2 = new se2(c4, s99.state);
    f2.readRange(l11.startDOM, l11.endDOM);
    let u5 = o4.from, d5 = null;
    (s99.inputState.lastKeyCode === 8 && s99.inputState.lastKeyTime > Date.now() - 100 || g2.android && f2.text.length < a2 - h3) && (u5 = o4.to, d5 = "end");
    let p5 = or(s99.state.doc.sliceString(h3, a2, X2), f2.text, u5 - h3, d5);
    p5 && (g2.chrome && s99.inputState.lastKeyCode == 13 && p5.toB == p5.from + 2 && f2.text.slice(p5.from, p5.toB) == X2 + X2 && p5.toB--, n22 = {
      from: h3 + p5.from,
      to: h3 + p5.toA,
      insert: m.of(f2.text.slice(p5.from, p5.toB).split(X2))
    }), r2 = hr(c4, h3);
  } else if (s99.hasFocus || !s99.state.facet(Nt)) {
    let l11 = s99.observer.selectionRange, { impreciseHead: h3, impreciseAnchor: a2 } = s99.docView, c4 = h3 && h3.node == l11.focusNode && h3.offset == l11.focusOffset || !pt(s99.contentDOM, l11.focusNode) ? s99.state.selection.main.head : s99.docView.posFromDOM(l11.focusNode, l11.focusOffset), f2 = a2 && a2.node == l11.anchorNode && a2.offset == l11.anchorOffset || !pt(s99.contentDOM, l11.anchorNode) ? s99.state.selection.main.anchor : s99.docView.posFromDOM(l11.anchorNode, l11.anchorOffset);
    (c4 != o4.head || f2 != o4.anchor) && (r2 = x.single(f2, c4));
  }
  if (!n22 && !r2) return false;
  if (!n22 && i9 && !o4.empty && r2 && r2.main.empty ? n22 = {
    from: o4.from,
    to: o4.to,
    insert: s99.state.doc.slice(o4.from, o4.to)
  } : n22 && n22.from >= o4.from && n22.to <= o4.to && (n22.from != o4.from || n22.to != o4.to) && o4.to - o4.from - (n22.to - n22.from) <= 4 ? n22 = {
    from: o4.from,
    to: o4.to,
    insert: s99.state.doc.slice(o4.from, n22.from).append(n22.insert).append(s99.state.doc.slice(n22.to, o4.to))
  } : (g2.mac || g2.android) && n22 && n22.from == n22.to && n22.from == o4.head - 1 && n22.insert.toString() == "." && (n22 = {
    from: o4.from,
    to: o4.to,
    insert: m.of([
      " "
    ])
  }), n22) {
    let l11 = s99.state;
    if (g2.ios && s99.inputState.flushIOSKey(s99) || g2.android && (n22.from == o4.from && n22.to == o4.to && n22.insert.length == 1 && n22.insert.lines == 2 && Ct(s99.contentDOM, "Enter", 13) || n22.from == o4.from - 1 && n22.to == o4.to && n22.insert.length == 0 && Ct(s99.contentDOM, "Backspace", 8) || n22.from == o4.from && n22.to == o4.to + 1 && n22.insert.length == 0 && Ct(s99.contentDOM, "Delete", 46))) return true;
    let h3 = n22.insert.toString();
    if (s99.state.facet(Ts).some((f2) => f2(s99, n22.from, n22.to, h3))) return true;
    s99.inputState.composing >= 0 && s99.inputState.composing++;
    let a2;
    if (n22.from >= o4.from && n22.to <= o4.to && n22.to - n22.from >= (o4.to - o4.from) / 3 && (!r2 || r2.main.empty && r2.main.from == n22.from + n22.insert.length) && s99.inputState.composing < 0) {
      let f2 = o4.from < n22.from ? l11.sliceDoc(o4.from, n22.from) : "", u5 = o4.to > n22.to ? l11.sliceDoc(n22.to, o4.to) : "";
      a2 = l11.replaceSelection(s99.state.toText(f2 + n22.insert.sliceString(0, void 0, s99.state.lineBreak) + u5));
    } else {
      let f2 = l11.changes(n22), u5 = r2 && !l11.selection.main.eq(r2.main) && r2.main.to <= f2.newLength ? r2.main : void 0;
      if (l11.selection.ranges.length > 1 && s99.inputState.composing >= 0 && n22.to <= o4.to && n22.to >= o4.to - 10) {
        let d5 = s99.state.sliceDoc(n22.from, n22.to), p5 = Ws(s99) || s99.state.doc.lineAt(o4.head), m9 = o4.to - n22.to, b9 = o4.to - o4.from;
        a2 = l11.changeByRange((y10) => {
          if (y10.from == o4.from && y10.to == o4.to) return {
            changes: f2,
            range: u5 || y10.map(f2)
          };
          let k13 = y10.to - m9, v8 = k13 - d5.length;
          if (y10.to - y10.from != b9 || s99.state.sliceDoc(v8, k13) != d5 || p5 && y10.to >= p5.from && y10.from <= p5.to) return {
            range: y10
          };
          let w11 = l11.changes({
            from: v8,
            to: k13,
            insert: n22.insert
          }), L10 = y10.to - o4.to;
          return {
            changes: w11,
            range: u5 ? x.range(Math.max(0, u5.anchor + L10), Math.max(0, u5.head + L10)) : y10.map(w11)
          };
        });
      } else a2 = {
        changes: f2,
        selection: u5 && l11.selection.replaceRange(u5)
      };
    }
    let c4 = "input.type";
    return s99.composing && (c4 += ".compose", s99.inputState.compositionFirstChange && (c4 += ".start", s99.inputState.compositionFirstChange = false)), s99.dispatch(a2, {
      scrollIntoView: true,
      userEvent: c4
    }), true;
  } else if (r2 && !r2.main.eq(o4)) {
    let l11 = false, h3 = "select";
    return s99.inputState.lastSelectionTime > Date.now() - 50 && (s99.inputState.lastSelectionOrigin == "select" && (l11 = true), h3 = s99.inputState.lastSelectionOrigin), s99.dispatch({
      selection: r2,
      scrollIntoView: l11,
      userEvent: h3
    }), true;
  } else return false;
}
function or(s99, t5, e4, i9) {
  let n22 = Math.min(s99.length, t5.length), r2 = 0;
  for (; r2 < n22 && s99.charCodeAt(r2) == t5.charCodeAt(r2); ) r2++;
  if (r2 == n22 && s99.length == t5.length) return null;
  let o4 = s99.length, l11 = t5.length;
  for (; o4 > 0 && l11 > 0 && s99.charCodeAt(o4 - 1) == t5.charCodeAt(l11 - 1); ) o4--, l11--;
  if (i9 == "end") {
    let h3 = Math.max(0, r2 - Math.min(o4, l11));
    e4 -= o4 + h3 - r2;
  }
  if (o4 < r2 && s99.length < t5.length) {
    let h3 = e4 <= r2 && e4 >= o4 ? r2 - e4 : 0;
    r2 -= h3, l11 = r2 + (l11 - o4), o4 = r2;
  } else if (l11 < r2) {
    let h3 = e4 <= r2 && e4 >= l11 ? r2 - e4 : 0;
    r2 -= h3, o4 = r2 + (o4 - l11), l11 = r2;
  }
  return {
    from: r2,
    toA: o4,
    toB: l11
  };
}
function lr(s99) {
  let t5 = [];
  if (s99.root.activeElement != s99.contentDOM) return t5;
  let { anchorNode: e4, anchorOffset: i9, focusNode: n22, focusOffset: r2 } = s99.observer.selectionRange;
  return e4 && (t5.push(new ne2(e4, i9)), (n22 != e4 || r2 != i9) && t5.push(new ne2(n22, r2))), t5;
}
function hr(s99, t5) {
  if (s99.length == 0) return null;
  let e4 = s99[0].pos, i9 = s99.length == 2 ? s99[1].pos : e4;
  return e4 > -1 && i9 > -1 ? x.single(e4 + t5, i9 + t5) : null;
}
var M2 = class s41 {
  constructor(t5 = {}) {
    this.plugins = [], this.pluginMap = /* @__PURE__ */ new Map(), this.editorAttrs = {}, this.contentAttrs = {}, this.bidiCache = [], this.destroyed = false, this.updateState = 2, this.measureScheduled = -1, this.measureRequests = [], this.contentDOM = document.createElement("div"), this.scrollDOM = document.createElement("div"), this.scrollDOM.tabIndex = -1, this.scrollDOM.className = "cm-scroller", this.scrollDOM.appendChild(this.contentDOM), this.announceDOM = document.createElement("div"), this.announceDOM.style.cssText = "position: absolute; top: -10000px", this.announceDOM.setAttribute("aria-live", "polite"), this.dom = document.createElement("div"), this.dom.appendChild(this.announceDOM), this.dom.appendChild(this.scrollDOM), this._dispatch = t5.dispatch || ((e4) => this.update([
      e4
    ])), this.dispatch = this.dispatch.bind(this), this.root = t5.root || wn(t5.parent) || document, this.viewState = new ce2(t5.state || I.create()), this.plugins = this.state.facet(bt).map((e4) => new Mt(e4));
    for (let e4 of this.plugins) e4.update(this);
    this.observer = new ii(this, (e4, i9, n22) => rr(this, e4, i9, n22), (e4) => {
      this.inputState.runScrollHandlers(this, e4), this.observer.intersecting && this.measure();
    }), this.inputState = new Ge2(this), this.inputState.ensureHandlers(this, this.plugins), this.docView = new re2(this), this.mountStyles(), this.updateAttrs(), this.updateState = 0, this.requestMeasure(), t5.parent && t5.parent.appendChild(this.dom);
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
  dispatch(...t5) {
    this._dispatch(t5.length == 1 && t5[0] instanceof S ? t5[0] : this.state.update(...t5));
  }
  update(t5) {
    if (this.updateState != 0) throw new Error("Calls to EditorView.update are not allowed while an update is in progress");
    let e4 = false, i9 = false, n22, r2 = this.state;
    for (let l11 of t5) {
      if (l11.startState != r2) throw new RangeError("Trying to update state with a transaction that doesn't start from the previous state.");
      r2 = l11.state;
    }
    if (this.destroyed) {
      this.viewState.state = r2;
      return;
    }
    if (this.observer.clear(), r2.facet(I.phrases) != this.state.facet(I.phrases)) return this.setState(r2);
    n22 = ie2.create(this, r2, t5);
    let o4 = this.viewState.scrollTarget;
    try {
      this.updateState = 2;
      for (let l11 of t5) {
        if (o4 && (o4 = o4.map(l11.changes)), l11.scrollIntoView) {
          let { main: h3 } = l11.state.selection;
          o4 = new ee2(h3.empty ? h3 : x.cursor(h3.head, h3.head > h3.anchor ? -1 : 1));
        }
        for (let h3 of l11.effects) h3.is(Di) && (o4 = h3.value);
      }
      this.viewState.update(n22, o4), this.bidiCache = fe2.update(this.bidiCache, n22.changes), n22.empty || (this.updatePlugins(n22), this.inputState.update(n22)), e4 = this.docView.update(n22), this.state.facet(yt) != this.styleModules && this.mountStyles(), i9 = this.updateAttrs(), this.showAnnouncements(t5), this.docView.updateSelection(e4, t5.some((l11) => l11.isUserEvent("select.pointer")));
    } finally {
      this.updateState = 0;
    }
    if (n22.startState.facet(Kt) != n22.state.facet(Kt) && (this.viewState.mustMeasureContent = true), (e4 || i9 || o4 || this.viewState.mustEnforceCursorAssoc || this.viewState.mustMeasureContent) && this.requestMeasure(), !n22.empty) for (let l11 of this.state.facet(ze2)) l11(n22);
  }
  setState(t5) {
    if (this.updateState != 0) throw new Error("Calls to EditorView.setState are not allowed while an update is in progress");
    if (this.destroyed) {
      this.viewState.state = t5;
      return;
    }
    this.updateState = 2;
    let e4 = this.hasFocus;
    try {
      for (let i9 of this.plugins) i9.destroy(this);
      this.viewState = new ce2(t5), this.plugins = t5.facet(bt).map((i9) => new Mt(i9)), this.pluginMap.clear();
      for (let i9 of this.plugins) i9.update(this);
      this.docView = new re2(this), this.inputState.ensureHandlers(this, this.plugins), this.mountStyles(), this.updateAttrs(), this.bidiCache = [];
    } finally {
      this.updateState = 0;
    }
    e4 && this.focus(), this.requestMeasure();
  }
  updatePlugins(t5) {
    let e4 = t5.startState.facet(bt), i9 = t5.state.facet(bt);
    if (e4 != i9) {
      let n22 = [];
      for (let r2 of i9) {
        let o4 = e4.indexOf(r2);
        if (o4 < 0) n22.push(new Mt(r2));
        else {
          let l11 = this.plugins[o4];
          l11.mustUpdate = t5, n22.push(l11);
        }
      }
      for (let r2 of this.plugins) r2.mustUpdate != t5 && r2.destroy(this);
      this.plugins = n22, this.pluginMap.clear(), this.inputState.ensureHandlers(this, this.plugins);
    } else for (let n22 of this.plugins) n22.mustUpdate = t5;
    for (let n22 = 0; n22 < this.plugins.length; n22++) this.plugins[n22].update(this);
  }
  measure(t5 = true) {
    if (this.destroyed) return;
    this.measureScheduled > -1 && cancelAnimationFrame(this.measureScheduled), this.measureScheduled = 0, t5 && this.observer.flush();
    let e4 = null;
    try {
      for (let i9 = 0; ; i9++) {
        this.updateState = 1;
        let n22 = this.viewport, r2 = this.viewState.measure(this);
        if (!r2 && !this.measureRequests.length && this.viewState.scrollTarget == null) break;
        if (i9 > 5) {
          console.warn(this.measureRequests.length ? "Measure loop restarted more than 5 times" : "Viewport failed to stabilize");
          break;
        }
        let o4 = [];
        r2 & 4 || ([this.measureRequests, o4] = [
          o4,
          this.measureRequests
        ]);
        let l11 = o4.map((f2) => {
          try {
            return f2.read(this);
          } catch (u5) {
            return Z2(this.state, u5), Yi;
          }
        }), h3 = ie2.create(this, this.state, []), a2 = false, c4 = false;
        h3.flags |= r2, e4 ? e4.flags |= r2 : e4 = h3, this.updateState = 2, h3.empty || (this.updatePlugins(h3), this.inputState.update(h3), this.updateAttrs(), a2 = this.docView.update(h3));
        for (let f2 = 0; f2 < o4.length; f2++) if (l11[f2] != Yi) try {
          let u5 = o4[f2];
          u5.write && u5.write(l11[f2], this);
        } catch (u5) {
          Z2(this.state, u5);
        }
        if (this.viewState.scrollTarget && (this.docView.scrollIntoView(this.viewState.scrollTarget), this.viewState.scrollTarget = null, c4 = true), a2 && this.docView.updateSelection(true), this.viewport.from == n22.from && this.viewport.to == n22.to && !c4 && this.measureRequests.length == 0) break;
      }
    } finally {
      this.updateState = 0, this.measureScheduled = -1;
    }
    if (e4 && !e4.empty) for (let i9 of this.state.facet(ze2)) i9(e4);
  }
  get themeClasses() {
    return ti + " " + (this.state.facet(Qe2) ? Xs : Us) + " " + this.state.facet(Kt);
  }
  updateAttrs() {
    let t5 = Ui(this, Rs, {
      class: "cm-editor" + (this.hasFocus ? " cm-focused " : " ") + this.themeClasses
    }), e4 = {
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
    this.state.readOnly && (e4["aria-readonly"] = "true"), Ui(this, bi, e4);
    let i9 = this.observer.ignore(() => {
      let n22 = Ve2(this.contentDOM, this.contentAttrs, e4), r2 = Ve2(this.dom, this.editorAttrs, t5);
      return n22 || r2;
    });
    return this.editorAttrs = t5, this.contentAttrs = e4, i9;
  }
  showAnnouncements(t5) {
    let e4 = true;
    for (let i9 of t5) for (let n22 of i9.effects) if (n22.is(s41.announce)) {
      e4 && (this.announceDOM.textContent = ""), e4 = false;
      let r2 = this.announceDOM.appendChild(document.createElement("div"));
      r2.textContent = n22.value;
    }
  }
  mountStyles() {
    this.styleModules = this.state.facet(yt), T2.mount(this.root, this.styleModules.concat(ir).reverse());
  }
  readMeasured() {
    if (this.updateState == 2) throw new Error("Reading the editor layout isn't allowed during an update");
    this.updateState == 0 && this.measureScheduled > -1 && this.measure(false);
  }
  requestMeasure(t5) {
    if (this.measureScheduled < 0 && (this.measureScheduled = requestAnimationFrame(() => this.measure())), t5) {
      if (t5.key != null) {
        for (let e4 = 0; e4 < this.measureRequests.length; e4++) if (this.measureRequests[e4].key === t5.key) {
          this.measureRequests[e4] = t5;
          return;
        }
      }
      this.measureRequests.push(t5);
    }
  }
  plugin(t5) {
    let e4 = this.pluginMap.get(t5);
    return (e4 === void 0 || e4 && e4.spec != t5) && this.pluginMap.set(t5, e4 = this.plugins.find((i9) => i9.spec == t5) || null), e4 && e4.update(this).value;
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
  elementAtHeight(t5) {
    return this.readMeasured(), this.viewState.elementAtHeight(t5);
  }
  lineBlockAtHeight(t5) {
    return this.readMeasured(), this.viewState.lineBlockAtHeight(t5);
  }
  get viewportLineBlocks() {
    return this.viewState.viewportLines;
  }
  lineBlockAt(t5) {
    return this.viewState.lineBlockAt(t5);
  }
  get contentHeight() {
    return this.viewState.contentHeight;
  }
  moveByChar(t5, e4, i9) {
    return ve2(this, t5, Bi(this, t5, e4, i9));
  }
  moveByGroup(t5, e4) {
    return ve2(this, t5, Bi(this, t5, e4, (i9) => zn(this, t5.head, i9)));
  }
  moveToLineBoundary(t5, e4, i9 = true) {
    return Wn(this, t5, e4, i9);
  }
  moveVertically(t5, e4, i9) {
    return ve2(this, t5, Fn(this, t5, e4, i9));
  }
  domAtPos(t5) {
    return this.docView.domAtPos(t5);
  }
  posAtDOM(t5, e4 = 0) {
    return this.docView.posFromDOM(t5, e4);
  }
  posAtCoords(t5, e4 = true) {
    return this.readMeasured(), Fs(this, t5, e4);
  }
  coordsAtPos(t5, e4 = 1) {
    this.readMeasured();
    let i9 = this.docView.coordsAt(t5, e4);
    if (!i9 || i9.left == i9.right) return i9;
    let n22 = this.state.doc.lineAt(t5), r2 = this.bidiSpans(n22), o4 = r2[Q2.find(r2, t5 - n22.from, -1, e4)];
    return ge2(i9, o4.dir == O2.LTR == e4 > 0);
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
  textDirectionAt(t5) {
    return !this.state.facet(Os) || t5 < this.viewport.from || t5 > this.viewport.to ? this.textDirection : (this.readMeasured(), this.docView.textDirectionAt(t5));
  }
  get lineWrapping() {
    return this.viewState.heightOracle.lineWrapping;
  }
  bidiSpans(t5) {
    if (t5.length > ar) return Ps(t5.length);
    let e4 = this.textDirectionAt(t5.from);
    for (let n22 of this.bidiCache) if (n22.from == t5.from && n22.dir == e4) return n22.order;
    let i9 = Hs(t5.text, e4);
    return this.bidiCache.push(new fe2(t5.from, t5.to, e4, i9)), i9;
  }
  get hasFocus() {
    var t5;
    return (document.hasFocus() || g2.safari && ((t5 = this.inputState) === null || t5 === void 0 ? void 0 : t5.lastContextMenu) > Date.now() - 3e4) && this.root.activeElement == this.contentDOM;
  }
  focus() {
    this.observer.ignore(() => {
      us(this.contentDOM), this.docView.updateSelection();
    });
  }
  destroy() {
    for (let t5 of this.plugins) t5.destroy(this);
    this.plugins = [], this.inputState.destroy(), this.dom.remove(), this.observer.destroy(), this.measureScheduled > -1 && cancelAnimationFrame(this.measureScheduled), this.destroyed = true;
  }
  static scrollIntoView(t5, e4 = {}) {
    return Di.of(new ee2(typeof t5 == "number" ? x.cursor(t5) : t5, e4.y, e4.x, e4.yMargin, e4.xMargin));
  }
  static domEventHandlers(t5) {
    return P2.define(() => ({}), {
      eventHandlers: t5
    });
  }
  static theme(t5, e4) {
    let i9 = T2.newName(), n22 = [
      Kt.of(i9),
      yt.of(ei(`.${i9}`, t5))
    ];
    return e4 && e4.dark && n22.push(Qe2.of(true)), n22;
  }
  static baseTheme(t5) {
    return lt.lowest(yt.of(ei("." + ti, t5, Js)));
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
  constructor(t5, e4, i9, n22) {
    this.from = t5, this.to = e4, this.dir = i9, this.order = n22;
  }
  static update(t5, e4) {
    if (e4.empty) return t5;
    let i9 = [], n22 = t5.length ? t5[t5.length - 1].dir : O2.LTR;
    for (let r2 = Math.max(0, t5.length - 10); r2 < t5.length; r2++) {
      let o4 = t5[r2];
      o4.dir == n22 && !e4.touchesRange(o4.from, o4.to) && i9.push(new s42(e4.mapPos(o4.from, 1), e4.mapPos(o4.to, -1), o4.dir, o4.order));
    }
    return i9;
  }
};
function Ui(s99, t5, e4) {
  for (let i9 = s99.state.facet(t5), n22 = i9.length - 1; n22 >= 0; n22--) {
    let r2 = i9[n22], o4 = typeof r2 == "function" ? r2(s99) : r2;
    o4 && Pe2(o4, e4);
  }
  return e4;
}
var cr = g2.mac ? "mac" : g2.windows ? "win" : g2.linux ? "linux" : "key";
function fr(s99, t5) {
  let e4 = s99.split(/-(?!$)/), i9 = e4[e4.length - 1];
  i9 == "Space" && (i9 = " ");
  let n22, r2, o4, l11;
  for (let h3 = 0; h3 < e4.length - 1; ++h3) {
    let a2 = e4[h3];
    if (/^(cmd|meta|m)$/i.test(a2)) l11 = true;
    else if (/^a(lt)?$/i.test(a2)) n22 = true;
    else if (/^(c|ctrl|control)$/i.test(a2)) r2 = true;
    else if (/^s(hift)?$/i.test(a2)) o4 = true;
    else if (/^mod$/i.test(a2)) t5 == "mac" ? l11 = true : r2 = true;
    else throw new Error("Unrecognized modifier name: " + a2);
  }
  return n22 && (i9 = "Alt-" + i9), r2 && (i9 = "Ctrl-" + i9), l11 && (i9 = "Meta-" + i9), o4 && (i9 = "Shift-" + i9), i9;
}
function Se2(s99, t5, e4) {
  return t5.altKey && (s99 = "Alt-" + s99), t5.ctrlKey && (s99 = "Ctrl-" + s99), t5.metaKey && (s99 = "Meta-" + s99), e4 !== false && t5.shiftKey && (s99 = "Shift-" + s99), s99;
}
var dr = M2.domEventHandlers({
  keydown(s99, t5) {
    return Qs(Zs(t5.state), s99, t5, "editor");
  }
});
var ur = y.define({
  enables: dr
});
var Xi = /* @__PURE__ */ new WeakMap();
function Zs(s99) {
  let t5 = s99.facet(ur), e4 = Xi.get(t5);
  return e4 || Xi.set(t5, e4 = mr(t5.reduce((i9, n22) => i9.concat(n22), []))), e4;
}
function Jr(s99, t5, e4) {
  return Qs(Zs(s99.state), t5, s99, e4);
}
var U2 = null;
var pr = 4e3;
function mr(s99, t5 = cr) {
  let e4 = /* @__PURE__ */ Object.create(null), i9 = /* @__PURE__ */ Object.create(null), n22 = (o4, l11) => {
    let h3 = i9[o4];
    if (h3 == null) i9[o4] = l11;
    else if (h3 != l11) throw new Error("Key binding " + o4 + " is used both as a regular binding and as a multi-stroke prefix");
  }, r2 = (o4, l11, h3, a2) => {
    let c4 = e4[o4] || (e4[o4] = /* @__PURE__ */ Object.create(null)), f2 = l11.split(/ (?!$)/).map((p5) => fr(p5, t5));
    for (let p5 = 1; p5 < f2.length; p5++) {
      let m9 = f2.slice(0, p5).join(" ");
      n22(m9, true), c4[m9] || (c4[m9] = {
        preventDefault: true,
        commands: [
          (b9) => {
            let y10 = U2 = {
              view: b9,
              prefix: m9,
              scope: o4
            };
            return setTimeout(() => {
              U2 == y10 && (U2 = null);
            }, pr), true;
          }
        ]
      });
    }
    let u5 = f2.join(" ");
    n22(u5, false);
    let d5 = c4[u5] || (c4[u5] = {
      preventDefault: false,
      commands: []
    });
    d5.commands.push(h3), a2 && (d5.preventDefault = true);
  };
  for (let o4 of s99) {
    let l11 = o4[t5] || o4.key;
    if (l11) for (let h3 of o4.scope ? o4.scope.split(" ") : [
      "editor"
    ]) r2(h3, l11, o4.run, o4.preventDefault), o4.shift && r2(h3, "Shift-" + l11, o4.shift, o4.preventDefault);
  }
  return e4;
}
function Qs(s99, t5, e4, i9) {
  let n22 = g(t5), r2 = n22.length == 1 && n22 != " ", o4 = "", l11 = false;
  U2 && U2.view == e4 && U2.scope == i9 && (o4 = U2.prefix + " ", (l11 = qs.indexOf(t5.keyCode) < 0) && (U2 = null));
  let h3 = (f2) => {
    if (f2) {
      for (let u5 of f2.commands) if (u5(e4)) return true;
      f2.preventDefault && (l11 = true);
    }
    return false;
  }, a2 = s99[i9], c4;
  if (a2) {
    if (h3(a2[o4 + Se2(n22, t5, !r2)])) return true;
    if (r2 && (t5.shiftKey || t5.altKey || t5.metaKey) && (c4 = t[t5.keyCode]) && c4 != n22) {
      if (h3(a2[o4 + Se2(c4, t5, true)])) return true;
    } else if (r2 && t5.shiftKey && h3(a2[o4 + Se2(n22, t5, true)])) return true;
  }
  return l11;
}
var tn = !g2.ios;
var vt = y.define({
  combine(s99) {
    return ht(s99, {
      cursorBlinkRate: 1200,
      drawRangeCursor: true
    }, {
      cursorBlinkRate: (t5, e4) => Math.min(t5, e4),
      drawRangeCursor: (t5, e4) => t5 || e4
    });
  }
});
function Zr(s99 = {}) {
  return [
    vt.of(s99),
    gr,
    br
  ];
}
var de2 = class {
  constructor(t5, e4, i9, n22, r2) {
    this.left = t5, this.top = e4, this.width = i9, this.height = n22, this.className = r2;
  }
  draw() {
    let t5 = document.createElement("div");
    return t5.className = this.className, this.adjust(t5), t5;
  }
  adjust(t5) {
    t5.style.left = this.left + "px", t5.style.top = this.top + "px", this.width >= 0 && (t5.style.width = this.width + "px"), t5.style.height = this.height + "px";
  }
  eq(t5) {
    return this.left == t5.left && this.top == t5.top && this.width == t5.width && this.height == t5.height && this.className == t5.className;
  }
};
var gr = P2.fromClass(class {
  constructor(s99) {
    this.view = s99, this.rangePieces = [], this.cursors = [], this.measureReq = {
      read: this.readPos.bind(this),
      write: this.drawSel.bind(this)
    }, this.selectionLayer = s99.scrollDOM.appendChild(document.createElement("div")), this.selectionLayer.className = "cm-selectionLayer", this.selectionLayer.setAttribute("aria-hidden", "true"), this.cursorLayer = s99.scrollDOM.appendChild(document.createElement("div")), this.cursorLayer.className = "cm-cursorLayer", this.cursorLayer.setAttribute("aria-hidden", "true"), s99.requestMeasure(this.measureReq), this.setBlinkRate();
  }
  setBlinkRate() {
    this.cursorLayer.style.animationDuration = this.view.state.facet(vt).cursorBlinkRate + "ms";
  }
  update(s99) {
    let t5 = s99.startState.facet(vt) != s99.state.facet(vt);
    (t5 || s99.selectionSet || s99.geometryChanged || s99.viewportChanged) && this.view.requestMeasure(this.measureReq), s99.transactions.some((e4) => e4.scrollIntoView) && (this.cursorLayer.style.animationName = this.cursorLayer.style.animationName == "cm-blink" ? "cm-blink2" : "cm-blink"), t5 && this.setBlinkRate();
  }
  readPos() {
    let { state: s99 } = this.view, t5 = s99.facet(vt), e4 = s99.selection.ranges.map((n22) => n22.empty ? [] : yr(this.view, n22)).reduce((n22, r2) => n22.concat(r2)), i9 = [];
    for (let n22 of s99.selection.ranges) {
      let r2 = n22 == s99.selection.main;
      if (n22.empty ? !r2 || tn : t5.drawRangeCursor) {
        let o4 = wr(this.view, n22, r2);
        o4 && i9.push(o4);
      }
    }
    return {
      rangePieces: e4,
      cursors: i9
    };
  }
  drawSel({ rangePieces: s99, cursors: t5 }) {
    if (s99.length != this.rangePieces.length || s99.some((e4, i9) => !e4.eq(this.rangePieces[i9]))) {
      this.selectionLayer.textContent = "";
      for (let e4 of s99) this.selectionLayer.appendChild(e4.draw());
      this.rangePieces = s99;
    }
    if (t5.length != this.cursors.length || t5.some((e4, i9) => !e4.eq(this.cursors[i9]))) {
      let e4 = this.cursorLayer.children;
      if (e4.length !== t5.length) {
        this.cursorLayer.textContent = "";
        for (let i9 of t5) this.cursorLayer.appendChild(i9.draw());
      } else t5.forEach((i9, n22) => i9.adjust(e4[n22]));
      this.cursors = t5;
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
function sn(s99) {
  let t5 = s99.scrollDOM.getBoundingClientRect();
  return {
    left: (s99.textDirection == O2.LTR ? t5.left : t5.right - s99.scrollDOM.clientWidth) - s99.scrollDOM.scrollLeft,
    top: t5.top - s99.scrollDOM.scrollTop
  };
}
function Ji(s99, t5, e4) {
  let i9 = x.cursor(t5);
  return {
    from: Math.max(e4.from, s99.moveToLineBoundary(i9, false, true).from),
    to: Math.min(e4.to, s99.moveToLineBoundary(i9, true, true).from),
    type: D2.Text
  };
}
function Zi(s99, t5) {
  let e4 = s99.lineBlockAt(t5);
  if (Array.isArray(e4.type)) {
    for (let i9 of e4.type) if (i9.to > t5 || i9.to == t5 && (i9.to == e4.to || i9.type == D2.Text)) return i9;
  }
  return e4;
}
function yr(s99, t5) {
  if (t5.to <= s99.viewport.from || t5.from >= s99.viewport.to) return [];
  let e4 = Math.max(t5.from, s99.viewport.from), i9 = Math.min(t5.to, s99.viewport.to), n22 = s99.textDirection == O2.LTR, r2 = s99.contentDOM, o4 = r2.getBoundingClientRect(), l11 = sn(s99), h3 = globalThis.getComputedStyle(r2.firstChild), a2 = o4.left + parseInt(h3.paddingLeft) + Math.min(0, parseInt(h3.textIndent)), c4 = o4.right - parseInt(h3.paddingRight), f2 = Zi(s99, e4), u5 = Zi(s99, i9), d5 = f2.type == D2.Text ? f2 : null, p5 = u5.type == D2.Text ? u5 : null;
  if (s99.lineWrapping && (d5 && (d5 = Ji(s99, e4, d5)), p5 && (p5 = Ji(s99, i9, p5))), d5 && p5 && d5.from == p5.from) return b9(y10(t5.from, t5.to, d5));
  {
    let v8 = d5 ? y10(t5.from, null, d5) : k13(f2, false), w11 = p5 ? y10(null, t5.to, p5) : k13(u5, true), L10 = [];
    return (d5 || f2).to < (p5 || u5).from - 1 ? L10.push(m9(a2, v8.bottom, c4, w11.top)) : v8.bottom < w11.top && s99.elementAtHeight((v8.bottom + w11.top) / 2).type == D2.Text && (v8.bottom = w11.top = (v8.bottom + w11.top) / 2), b9(v8).concat(L10).concat(b9(w11));
  }
  function m9(v8, w11, L10, j12) {
    return new de2(v8 - l11.left, w11 - l11.top - 0.01, L10 - v8, j12 - w11 + 0.01, "cm-selectionBackground");
  }
  function b9({ top: v8, bottom: w11, horizontal: L10 }) {
    let j12 = [];
    for (let G12 = 0; G12 < L10.length; G12 += 2) j12.push(m9(L10[G12], v8, L10[G12 + 1], w11));
    return j12;
  }
  function y10(v8, w11, L10) {
    let j12 = 1e9, G12 = -1e9, Wt7 = [];
    function vi2(st8, $9, lt7, nt7, mt8) {
      let _11 = s99.coordsAtPos(st8, st8 == L10.to ? -2 : 2), Y11 = s99.coordsAtPos(lt7, lt7 == L10.from ? 2 : -2);
      j12 = Math.min(_11.top, Y11.top, j12), G12 = Math.max(_11.bottom, Y11.bottom, G12), mt8 == O2.LTR ? Wt7.push(n22 && $9 ? a2 : _11.left, n22 && nt7 ? c4 : Y11.right) : Wt7.push(!n22 && nt7 ? a2 : Y11.left, !n22 && $9 ? c4 : _11.right);
    }
    let zt6 = v8 ?? L10.from, Ft7 = w11 ?? L10.to;
    for (let st8 of s99.visibleRanges) if (st8.to > zt6 && st8.from < Ft7) for (let $9 = Math.max(st8.from, zt6), lt7 = Math.min(st8.to, Ft7); ; ) {
      let nt7 = s99.state.doc.lineAt($9);
      for (let mt8 of s99.bidiSpans(nt7)) {
        let _11 = mt8.from + nt7.from, Y11 = mt8.to + nt7.from;
        if (_11 >= lt7) break;
        Y11 > $9 && vi2(Math.max(_11, $9), v8 == null && _11 <= zt6, Math.min(Y11, lt7), w11 == null && Y11 >= Ft7, mt8.dir);
      }
      if ($9 = nt7.to + 1, $9 >= lt7) break;
    }
    return Wt7.length == 0 && vi2(zt6, v8 == null, Ft7, w11 == null, s99.textDirection), {
      top: j12,
      bottom: G12,
      horizontal: Wt7
    };
  }
  function k13(v8, w11) {
    let L10 = o4.top + (w11 ? v8.top : v8.bottom);
    return {
      top: L10,
      bottom: L10,
      horizontal: []
    };
  }
}
function wr(s99, t5, e4) {
  let i9 = s99.coordsAtPos(t5.head, t5.assoc || 1);
  if (!i9) return null;
  let n22 = sn(s99);
  return new de2(i9.left - n22.left, i9.top - n22.top, -1, i9.bottom - i9.top, e4 ? "cm-cursor cm-cursor-primary" : "cm-cursor cm-cursor-secondary");
}
var nn = v.define({
  map(s99, t5) {
    return s99 == null ? null : t5.mapPos(s99);
  }
});
var xt = $.define({
  create() {
    return null;
  },
  update(s99, t5) {
    return s99 != null && (s99 = t5.changes.mapPos(s99)), t5.effects.reduce((e4, i9) => i9.is(nn) ? i9.value : e4, s99);
  }
});
var vr = P2.fromClass(class {
  constructor(s99) {
    this.view = s99, this.cursor = null, this.measureReq = {
      read: this.readPos.bind(this),
      write: this.drawCursor.bind(this)
    };
  }
  update(s99) {
    var t5;
    let e4 = s99.state.field(xt);
    e4 == null ? this.cursor != null && ((t5 = this.cursor) === null || t5 === void 0 || t5.remove(), this.cursor = null) : (this.cursor || (this.cursor = this.view.scrollDOM.appendChild(document.createElement("div")), this.cursor.className = "cm-dropCursor"), (s99.startState.field(xt) != e4 || s99.docChanged || s99.geometryChanged) && this.view.requestMeasure(this.measureReq));
  }
  readPos() {
    let s99 = this.view.state.field(xt), t5 = s99 != null && this.view.coordsAtPos(s99);
    if (!t5) return null;
    let e4 = this.view.scrollDOM.getBoundingClientRect();
    return {
      left: t5.left - e4.left + this.view.scrollDOM.scrollLeft,
      top: t5.top - e4.top + this.view.scrollDOM.scrollTop,
      height: t5.bottom - t5.top
    };
  }
  drawCursor(s99) {
    this.cursor && (s99 ? (this.cursor.style.left = s99.left + "px", this.cursor.style.top = s99.top + "px", this.cursor.style.height = s99.height + "px") : this.cursor.style.left = "-100000px");
  }
  destroy() {
    this.cursor && this.cursor.remove();
  }
  setDropPos(s99) {
    this.view.state.field(xt) != s99 && this.view.dispatch({
      effects: nn.of(s99)
    });
  }
}, {
  eventHandlers: {
    dragover(s99) {
      this.setDropPos(this.view.posAtCoords({
        x: s99.clientX,
        y: s99.clientY
      }));
    },
    dragleave(s99) {
      (s99.target == this.view.contentDOM || !this.view.contentDOM.contains(s99.relatedTarget)) && this.setDropPos(null);
    },
    dragend() {
      this.setDropPos(null);
    },
    drop() {
      this.setDropPos(null);
    }
  }
});
function Qr() {
  return [
    xt,
    vr
  ];
}
function Qi(s99, t5, e4, i9, n22) {
  t5.lastIndex = 0;
  for (let r2 = s99.iterRange(e4, i9), o4 = e4, l11; !r2.next().done; o4 += r2.value.length) if (!r2.lineBreak) for (; l11 = t5.exec(r2.value); ) n22(o4 + l11.index, o4 + l11.index + l11[0].length, l11);
}
function xr(s99, t5) {
  let e4 = s99.visibleRanges;
  if (e4.length == 1 && e4[0].from == s99.viewport.from && e4[0].to == s99.viewport.to) return e4;
  let i9 = [];
  for (let { from: n22, to: r2 } of e4) n22 = Math.max(s99.state.doc.lineAt(n22).from, n22 - t5), r2 = Math.min(s99.state.doc.lineAt(r2).to, r2 + t5), i9.length && i9[i9.length - 1].to >= n22 ? i9[i9.length - 1].to = r2 : i9.push({
    from: n22,
    to: r2
  });
  return i9;
}
var si = class {
  constructor(t5) {
    let { regexp: e4, decoration: i9, boundary: n22, maxLength: r2 = 1e3 } = t5;
    if (!e4.global) throw new RangeError("The regular expression given to MatchDecorator should have its 'g' flag set");
    this.regexp = e4, this.getDeco = typeof i9 == "function" ? i9 : () => i9, this.boundary = n22, this.maxLength = r2;
  }
  createDeco(t5) {
    let e4 = new se();
    for (let { from: i9, to: n22 } of xr(t5, this.maxLength)) Qi(t5.state.doc, this.regexp, i9, n22, (r2, o4, l11) => e4.add(r2, o4, this.getDeco(l11, t5, r2)));
    return e4.finish();
  }
  updateDeco(t5, e4) {
    let i9 = 1e9, n22 = -1;
    return t5.docChanged && t5.changes.iterChanges((r2, o4, l11, h3) => {
      h3 > t5.view.viewport.from && l11 < t5.view.viewport.to && (i9 = Math.min(l11, i9), n22 = Math.max(h3, n22));
    }), t5.viewportChanged || n22 - i9 > 1e3 ? this.createDeco(t5.view) : n22 > -1 ? this.updateRange(t5.view, e4.map(t5.changes), i9, n22) : e4;
  }
  updateRange(t5, e4, i9, n22) {
    for (let r2 of t5.visibleRanges) {
      let o4 = Math.max(r2.from, i9), l11 = Math.min(r2.to, n22);
      if (l11 > o4) {
        let h3 = t5.state.doc.lineAt(o4), a2 = h3.to < l11 ? t5.state.doc.lineAt(l11) : h3, c4 = Math.max(r2.from, h3.from), f2 = Math.min(r2.to, a2.to);
        if (this.boundary) {
          for (; o4 > h3.from; o4--) if (this.boundary.test(h3.text[o4 - 1 - h3.from])) {
            c4 = o4;
            break;
          }
          for (; l11 < a2.to; l11++) if (this.boundary.test(a2.text[l11 - a2.from])) {
            f2 = l11;
            break;
          }
        }
        let u5 = [], d5;
        if (h3 == a2) for (this.regexp.lastIndex = c4 - h3.from; (d5 = this.regexp.exec(h3.text)) && d5.index < f2 - h3.from; ) {
          let p5 = d5.index + h3.from;
          u5.push(this.getDeco(d5, t5, p5).range(p5, p5 + d5[0].length));
        }
        else Qi(t5.state.doc, this.regexp, c4, f2, (p5, m9, b9) => u5.push(this.getDeco(b9, t5, p5).range(p5, m9)));
        e4 = e4.update({
          filterFrom: c4,
          filterTo: f2,
          filter: (p5, m9) => p5 < c4 || m9 > f2,
          add: u5
        });
      }
    }
    return e4;
  }
};
var ni = /x/.unicode != null ? "gu" : "g";
var Sr = new RegExp(`[\0-\b
-\x7F-\x9F\xAD\u061C\u200B\u200E\u200F\u2028\u2029\u202D\u202E\uFEFF\uFFF9-\uFFFC]`, ni);
var Cr = {
  0: "null",
  7: "bell",
  8: "backspace",
  10: "newline",
  11: "vertical tab",
  13: "carriage return",
  27: "escape",
  8203: "zero width space",
  8204: "zero width non-joiner",
  8205: "zero width joiner",
  8206: "left-to-right mark",
  8207: "right-to-left mark",
  8232: "line separator",
  8237: "left-to-right override",
  8238: "right-to-left override",
  8233: "paragraph separator",
  65279: "zero width no-break space",
  65532: "object replacement"
};
var Ce2 = null;
function Mr() {
  var s99;
  if (Ce2 == null && typeof document < "u" && document.body) {
    let t5 = document.body.style;
    Ce2 = ((s99 = t5.tabSize) !== null && s99 !== void 0 ? s99 : t5.MozTabSize) != null;
  }
  return Ce2 || false;
}
var Gt = y.define({
  combine(s99) {
    let t5 = ht(s99, {
      render: null,
      specialChars: Sr,
      addSpecialChars: null
    });
    return (t5.replaceTabs = !Mr()) && (t5.specialChars = new RegExp("	|" + t5.specialChars.source, ni)), t5.addSpecialChars && (t5.specialChars = new RegExp(t5.specialChars.source + "|" + t5.addSpecialChars.source, ni)), t5;
  }
});
function to(s99 = {}) {
  return [
    Gt.of(s99),
    kr()
  ];
}
var ts = null;
function kr() {
  return ts || (ts = P2.fromClass(class {
    constructor(s99) {
      this.view = s99, this.decorations = C2.none, this.decorationCache = /* @__PURE__ */ Object.create(null), this.decorator = this.makeDecorator(s99.state.facet(Gt)), this.decorations = this.decorator.createDeco(s99);
    }
    makeDecorator(s99) {
      return new si({
        regexp: s99.specialChars,
        decoration: (t5, e4, i9) => {
          let { doc: n22 } = e4.state, r2 = he(t5[0], 0);
          if (r2 == 9) {
            let o4 = n22.lineAt(i9), l11 = e4.state.tabSize, h3 = ot(o4.text, l11, i9 - o4.from);
            return C2.replace({
              widget: new oi((l11 - h3 % l11) * this.view.defaultCharacterWidth)
            });
          }
          return this.decorationCache[r2] || (this.decorationCache[r2] = C2.replace({
            widget: new ri(s99, r2)
          }));
        },
        boundary: s99.replaceTabs ? void 0 : /[^]/
      });
    }
    update(s99) {
      let t5 = s99.state.facet(Gt);
      s99.startState.facet(Gt) != t5 ? (this.decorator = this.makeDecorator(t5), this.decorations = this.decorator.createDeco(s99.view)) : this.decorations = this.decorator.updateDeco(s99, this.decorations);
    }
  }, {
    decorations: (s99) => s99.decorations
  }));
}
var Ar = "\u2022";
function Dr(s99) {
  return s99 >= 32 ? Ar : s99 == 10 ? "\u2424" : String.fromCharCode(9216 + s99);
}
var ri = class extends K2 {
  constructor(t5, e4) {
    super(), this.options = t5, this.code = e4;
  }
  eq(t5) {
    return t5.code == this.code;
  }
  toDOM(t5) {
    let e4 = Dr(this.code), i9 = t5.state.phrase("Control character") + " " + (Cr[this.code] || "0x" + this.code.toString(16)), n22 = this.options.render && this.options.render(this.code, i9, e4);
    if (n22) return n22;
    let r2 = document.createElement("span");
    return r2.textContent = e4, r2.title = i9, r2.setAttribute("aria-label", i9), r2.className = "cm-specialChar", r2;
  }
  ignoreEvent() {
    return false;
  }
};
var oi = class extends K2 {
  constructor(t5) {
    super(), this.width = t5;
  }
  eq(t5) {
    return t5.width == this.width;
  }
  toDOM() {
    let t5 = document.createElement("span");
    return t5.textContent = "	", t5.className = "cm-tab", t5.style.width = this.width + "px", t5;
  }
  ignoreEvent() {
    return false;
  }
};
var es = P2.fromClass(class {
  constructor() {
    this.height = 1e3, this.attrs = {
      style: "padding-bottom: 1000px"
    };
  }
  update(s99) {
    let t5 = s99.view.viewState.editorHeight - s99.view.defaultLineHeight;
    t5 != this.height && (this.height = t5, this.attrs = {
      style: `padding-bottom: ${t5}px`
    });
  }
});
function io() {
  return Or;
}
var Tr = C2.line({
  class: "cm-activeLine"
});
var Or = P2.fromClass(class {
  constructor(s99) {
    this.decorations = this.getDeco(s99);
  }
  update(s99) {
    (s99.docChanged || s99.selectionSet) && (this.decorations = this.getDeco(s99.view));
  }
  getDeco(s99) {
    let t5 = -1, e4 = [];
    for (let i9 of s99.state.selection.ranges) {
      if (!i9.empty) return C2.none;
      let n22 = s99.lineBlockAt(i9.head);
      n22.from > t5 && (e4.push(Tr.range(n22.from)), t5 = n22.from);
    }
    return C2.set(e4);
  }
}, {
  decorations: (s99) => s99.decorations
});
var hi = 2e3;
function Rr(s99, t5, e4) {
  let i9 = Math.min(t5.line, e4.line), n22 = Math.max(t5.line, e4.line), r2 = [];
  if (t5.off > hi || e4.off > hi || t5.col < 0 || e4.col < 0) {
    let o4 = Math.min(t5.off, e4.off), l11 = Math.max(t5.off, e4.off);
    for (let h3 = i9; h3 <= n22; h3++) {
      let a2 = s99.doc.line(h3);
      a2.length <= l11 && r2.push(x.range(a2.from + o4, a2.to + l11));
    }
  } else {
    let o4 = Math.min(t5.col, e4.col), l11 = Math.max(t5.col, e4.col);
    for (let h3 = i9; h3 <= n22; h3++) {
      let a2 = s99.doc.line(h3), c4 = at(a2.text, o4, s99.tabSize, true);
      if (c4 > -1) {
        let f2 = at(a2.text, l11, s99.tabSize);
        r2.push(x.range(a2.from + c4, a2.from + f2));
      }
    }
  }
  return r2;
}
function Lr(s99, t5) {
  let e4 = s99.coordsAtPos(s99.viewport.from);
  return e4 ? Math.round(Math.abs((e4.left - t5) / s99.defaultCharacterWidth)) : -1;
}
function is(s99, t5) {
  let e4 = s99.posAtCoords({
    x: t5.clientX,
    y: t5.clientY
  }, false), i9 = s99.state.doc.lineAt(e4), n22 = e4 - i9.from, r2 = n22 > hi ? -1 : n22 == i9.length ? Lr(s99, t5.clientX) : ot(i9.text, s99.state.tabSize, e4 - i9.from);
  return {
    line: i9.number,
    col: r2,
    off: n22
  };
}
function Er(s99, t5) {
  let e4 = is(s99, t5), i9 = s99.state.selection;
  return e4 ? {
    update(n22) {
      if (n22.docChanged) {
        let r2 = n22.changes.mapPos(n22.startState.doc.line(e4.line).from), o4 = n22.state.doc.lineAt(r2);
        e4 = {
          line: o4.number,
          col: e4.col,
          off: Math.min(e4.off, o4.length)
        }, i9 = i9.map(n22.changes);
      }
    },
    get(n22, r2, o4) {
      let l11 = is(s99, n22);
      if (!l11) return i9;
      let h3 = Rr(s99.state, e4, l11);
      return h3.length ? o4 ? x.create(h3.concat(i9.ranges)) : x.create(h3) : i9;
    }
  } : null;
}
function no(s99) {
  let t5 = s99?.eventFilter || ((e4) => e4.altKey && e4.button == 0);
  return M2.mouseSelectionStyle.of((e4, i9) => t5(i9) ? Er(e4, i9) : null);
}
var Br = {
  Alt: [
    18,
    (s99) => s99.altKey
  ],
  Control: [
    17,
    (s99) => s99.ctrlKey
  ],
  Shift: [
    16,
    (s99) => s99.shiftKey
  ],
  Meta: [
    91,
    (s99) => s99.metaKey
  ]
};
var Hr = {
  style: "cursor: crosshair"
};
function ro(s99 = {}) {
  let [t5, e4] = Br[s99.key || "Alt"], i9 = P2.fromClass(class {
    constructor(n22) {
      this.view = n22, this.isDown = false;
    }
    set(n22) {
      this.isDown != n22 && (this.isDown = n22, this.view.update([]));
    }
  }, {
    eventHandlers: {
      keydown(n22) {
        this.set(n22.keyCode == t5 || e4(n22));
      },
      keyup(n22) {
        (n22.keyCode == t5 || !e4(n22)) && this.set(false);
      }
    }
  });
  return [
    i9,
    M2.contentAttributes.of((n22) => {
      var r2;
      return !((r2 = n22.plugin(i9)) === null || r2 === void 0) && r2.isDown ? Hr : null;
    })
  ];
}
var Me2 = "-10000px";
var ue2 = class {
  constructor(t5, e4, i9) {
    this.facet = e4, this.createTooltipView = i9, this.input = t5.state.facet(e4), this.tooltips = this.input.filter((n22) => n22), this.tooltipViews = this.tooltips.map(i9);
  }
  update(t5) {
    let e4 = t5.state.facet(this.facet), i9 = e4.filter((r2) => r2);
    if (e4 === this.input) {
      for (let r2 of this.tooltipViews) r2.update && r2.update(t5);
      return false;
    }
    let n22 = [];
    for (let r2 = 0; r2 < i9.length; r2++) {
      let o4 = i9[r2], l11 = -1;
      if (o4) {
        for (let h3 = 0; h3 < this.tooltips.length; h3++) {
          let a2 = this.tooltips[h3];
          a2 && a2.create == o4.create && (l11 = h3);
        }
        if (l11 < 0) n22[r2] = this.createTooltipView(o4);
        else {
          let h3 = n22[r2] = this.tooltipViews[l11];
          h3.update && h3.update(t5);
        }
      }
    }
    for (let r2 of this.tooltipViews) n22.indexOf(r2) < 0 && r2.dom.remove();
    return this.input = e4, this.tooltips = i9, this.tooltipViews = n22, true;
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
  combine: (s99) => {
    var t5, e4, i9;
    return {
      position: g2.ios ? "absolute" : ((t5 = s99.find((n22) => n22.position)) === null || t5 === void 0 ? void 0 : t5.position) || "fixed",
      parent: ((e4 = s99.find((n22) => n22.parent)) === null || e4 === void 0 ? void 0 : e4.parent) || null,
      tooltipSpace: ((i9 = s99.find((n22) => n22.tooltipSpace)) === null || i9 === void 0 ? void 0 : i9.tooltipSpace) || Pr
    };
  }
});
var wi = P2.fromClass(class {
  constructor(s99) {
    var t5;
    this.view = s99, this.inView = true, this.lastTransaction = 0, this.measureTimeout = -1;
    let e4 = s99.state.facet($t);
    this.position = e4.position, this.parent = e4.parent, this.classes = s99.themeClasses, this.createContainer(), this.measureReq = {
      read: this.readMeasure.bind(this),
      write: this.writeMeasure.bind(this),
      key: this
    }, this.manager = new ue2(s99, rn, (i9) => this.createTooltip(i9)), this.intersectionObserver = typeof IntersectionObserver == "function" ? new IntersectionObserver((i9) => {
      Date.now() > this.lastTransaction - 50 && i9.length > 0 && i9[i9.length - 1].intersectionRatio < 1 && this.measureSoon();
    }, {
      threshold: [
        1
      ]
    }) : null, this.observeIntersection(), (t5 = s99.dom.ownerDocument.defaultView) === null || t5 === void 0 || t5.addEventListener("resize", this.measureSoon = this.measureSoon.bind(this)), this.maybeMeasure();
  }
  createContainer() {
    this.parent ? (this.container = document.createElement("div"), this.container.style.position = "relative", this.container.className = this.view.themeClasses, this.parent.appendChild(this.container)) : this.container = this.view.dom;
  }
  observeIntersection() {
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect();
      for (let s99 of this.manager.tooltipViews) this.intersectionObserver.observe(s99.dom);
    }
  }
  measureSoon() {
    this.measureTimeout < 0 && (this.measureTimeout = setTimeout(() => {
      this.measureTimeout = -1, this.maybeMeasure();
    }, 50));
  }
  update(s99) {
    s99.transactions.length && (this.lastTransaction = Date.now());
    let t5 = this.manager.update(s99);
    t5 && this.observeIntersection();
    let e4 = t5 || s99.geometryChanged, i9 = s99.state.facet($t);
    if (i9.position != this.position) {
      this.position = i9.position;
      for (let n22 of this.manager.tooltipViews) n22.dom.style.position = this.position;
      e4 = true;
    }
    if (i9.parent != this.parent) {
      this.parent && this.container.remove(), this.parent = i9.parent, this.createContainer();
      for (let n22 of this.manager.tooltipViews) this.container.appendChild(n22.dom);
      e4 = true;
    } else this.parent && this.view.themeClasses != this.classes && (this.classes = this.container.className = this.view.themeClasses);
    e4 && this.maybeMeasure();
  }
  createTooltip(s99) {
    let t5 = s99.create(this.view);
    if (t5.dom.classList.add("cm-tooltip"), s99.arrow && !t5.dom.querySelector(".cm-tooltip > .cm-tooltip-arrow")) {
      let e4 = document.createElement("div");
      e4.className = "cm-tooltip-arrow", t5.dom.appendChild(e4);
    }
    return t5.dom.style.position = this.position, t5.dom.style.top = Me2, this.container.appendChild(t5.dom), t5.mount && t5.mount(this.view), t5;
  }
  destroy() {
    var s99, t5;
    (s99 = this.view.dom.ownerDocument.defaultView) === null || s99 === void 0 || s99.removeEventListener("resize", this.measureSoon);
    for (let { dom: e4 } of this.manager.tooltipViews) e4.remove();
    (t5 = this.intersectionObserver) === null || t5 === void 0 || t5.disconnect(), clearTimeout(this.measureTimeout);
  }
  readMeasure() {
    let s99 = this.view.dom.getBoundingClientRect();
    return {
      editor: s99,
      parent: this.parent ? this.container.getBoundingClientRect() : s99,
      pos: this.manager.tooltips.map((t5, e4) => {
        let i9 = this.manager.tooltipViews[e4];
        return i9.getCoords ? i9.getCoords(t5.pos) : this.view.coordsAtPos(t5.pos);
      }),
      size: this.manager.tooltipViews.map(({ dom: t5 }) => t5.getBoundingClientRect()),
      space: this.view.state.facet($t).tooltipSpace(this.view)
    };
  }
  writeMeasure(s99) {
    let { editor: t5, space: e4 } = s99, i9 = [];
    for (let n22 = 0; n22 < this.manager.tooltips.length; n22++) {
      let r2 = this.manager.tooltips[n22], o4 = this.manager.tooltipViews[n22], { dom: l11 } = o4, h3 = s99.pos[n22], a2 = s99.size[n22];
      if (!h3 || h3.bottom <= Math.max(t5.top, e4.top) || h3.top >= Math.min(t5.bottom, e4.bottom) || h3.right < Math.max(t5.left, e4.left) - 0.1 || h3.left > Math.min(t5.right, e4.right) + 0.1) {
        l11.style.top = Me2;
        continue;
      }
      let c4 = r2.arrow ? o4.dom.querySelector(".cm-tooltip-arrow") : null, f2 = c4 ? 7 : 0, u5 = a2.right - a2.left, d5 = a2.bottom - a2.top, p5 = o4.offset || Nr, m9 = this.view.textDirection == O2.LTR, b9 = a2.width > e4.right - e4.left ? m9 ? e4.left : e4.right - a2.width : m9 ? Math.min(h3.left - (c4 ? 14 : 0) + p5.x, e4.right - u5) : Math.max(e4.left, h3.left - u5 + (c4 ? 14 : 0) - p5.x), y10 = !!r2.above;
      !r2.strictSide && (y10 ? h3.top - (a2.bottom - a2.top) - p5.y < e4.top : h3.bottom + (a2.bottom - a2.top) + p5.y > e4.bottom) && y10 == e4.bottom - h3.bottom > h3.top - e4.top && (y10 = !y10);
      let k13 = y10 ? h3.top - d5 - f2 - p5.y : h3.bottom + f2 + p5.y, v8 = b9 + u5;
      if (o4.overlap !== true) for (let w11 of i9) w11.left < v8 && w11.right > b9 && w11.top < k13 + d5 && w11.bottom > k13 && (k13 = y10 ? w11.top - d5 - 2 - f2 : w11.bottom + f2 + 2);
      this.position == "absolute" ? (l11.style.top = k13 - s99.parent.top + "px", l11.style.left = b9 - s99.parent.left + "px") : (l11.style.top = k13 + "px", l11.style.left = b9 + "px"), c4 && (c4.style.left = `${h3.left + (m9 ? p5.x : -p5.x) - (b9 + 14 - 7)}px`), o4.overlap !== true && i9.push({
        left: b9,
        top: k13,
        right: v8,
        bottom: k13 + d5
      }), l11.classList.toggle("cm-tooltip-above", y10), l11.classList.toggle("cm-tooltip-below", !y10), o4.positioned && o4.positioned();
    }
  }
  maybeMeasure() {
    if (this.manager.tooltips.length && (this.view.inView && this.view.requestMeasure(this.measureReq), this.inView != this.view.inView && (this.inView = this.view.inView, !this.inView))) for (let s99 of this.manager.tooltipViews) s99.dom.style.top = Me2;
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
  constructor(t5) {
    this.view = t5, this.mounted = false, this.dom = document.createElement("div"), this.dom.classList.add("cm-tooltip-hover"), this.manager = new ue2(t5, Pt, (e4) => this.createHostedView(e4));
  }
  static create(t5) {
    return new s43(t5);
  }
  createHostedView(t5) {
    let e4 = t5.create(this.view);
    return e4.dom.classList.add("cm-tooltip-section"), this.dom.appendChild(e4.dom), this.mounted && e4.mount && e4.mount(this.view), e4;
  }
  mount(t5) {
    for (let e4 of this.manager.tooltipViews) e4.mount && e4.mount(t5);
    this.mounted = true;
  }
  positioned() {
    for (let t5 of this.manager.tooltipViews) t5.positioned && t5.positioned();
  }
  update(t5) {
    this.manager.update(t5);
  }
};
var Wr = rn.compute([
  Pt
], (s99) => {
  let t5 = s99.facet(Pt).filter((e4) => e4);
  return t5.length === 0 ? null : {
    pos: Math.min(...t5.map((e4) => e4.pos)),
    end: Math.max(...t5.filter((e4) => e4.end != null).map((e4) => e4.end)),
    create: ai.create,
    above: t5[0].above,
    arrow: t5.some((e4) => e4.arrow)
  };
});
var ci = class {
  constructor(t5, e4, i9, n22, r2) {
    this.view = t5, this.source = e4, this.field = i9, this.setHover = n22, this.hoverTime = r2, this.hoverTimeout = -1, this.restartTimeout = -1, this.pending = null, this.lastMove = {
      x: 0,
      y: 0,
      target: t5.dom,
      time: 0
    }, this.checkHover = this.checkHover.bind(this), t5.dom.addEventListener("mouseleave", this.mouseleave = this.mouseleave.bind(this)), t5.dom.addEventListener("mousemove", this.mousemove = this.mousemove.bind(this));
  }
  update() {
    this.pending && (this.pending = null, clearTimeout(this.restartTimeout), this.restartTimeout = setTimeout(() => this.startHover(), 20));
  }
  get active() {
    return this.view.state.field(this.field);
  }
  checkHover() {
    if (this.hoverTimeout = -1, this.active) return;
    let t5 = Date.now() - this.lastMove.time;
    t5 < this.hoverTime ? this.hoverTimeout = setTimeout(this.checkHover, this.hoverTime - t5) : this.startHover();
  }
  startHover() {
    clearTimeout(this.restartTimeout);
    let { lastMove: t5 } = this, e4 = this.view.contentDOM.contains(t5.target) ? this.view.posAtCoords(t5) : null;
    if (e4 == null) return;
    let i9 = this.view.coordsAtPos(e4);
    if (i9 == null || t5.y < i9.top || t5.y > i9.bottom || t5.x < i9.left - this.view.defaultCharacterWidth || t5.x > i9.right + this.view.defaultCharacterWidth) return;
    let n22 = this.view.bidiSpans(this.view.state.doc.lineAt(e4)).find((l11) => l11.from <= e4 && l11.to >= e4), r2 = n22 && n22.dir == O2.RTL ? -1 : 1, o4 = this.source(this.view, e4, t5.x < i9.left ? -r2 : r2);
    if (o4?.then) {
      let l11 = this.pending = {
        pos: e4
      };
      o4.then((h3) => {
        this.pending == l11 && (this.pending = null, h3 && this.view.dispatch({
          effects: this.setHover.of(h3)
        }));
      }, (h3) => Z2(this.view.state, h3, "hover tooltip"));
    } else o4 && this.view.dispatch({
      effects: this.setHover.of(o4)
    });
  }
  mousemove(t5) {
    var e4;
    this.lastMove = {
      x: t5.clientX,
      y: t5.clientY,
      target: t5.target,
      time: Date.now()
    }, this.hoverTimeout < 0 && (this.hoverTimeout = setTimeout(this.checkHover, this.hoverTime));
    let i9 = this.active;
    if (i9 && !zr(this.lastMove.target) || this.pending) {
      let { pos: n22 } = i9 || this.pending, r2 = (e4 = i9?.end) !== null && e4 !== void 0 ? e4 : n22;
      (n22 == r2 ? this.view.posAtCoords(this.lastMove) != n22 : !Fr(this.view, n22, r2, t5.clientX, t5.clientY, 6)) && (this.view.dispatch({
        effects: this.setHover.of(null)
      }), this.pending = null);
    }
  }
  mouseleave() {
    clearTimeout(this.hoverTimeout), this.hoverTimeout = -1, this.active && this.view.dispatch({
      effects: this.setHover.of(null)
    });
  }
  destroy() {
    clearTimeout(this.hoverTimeout), this.view.dom.removeEventListener("mouseleave", this.mouseleave), this.view.dom.removeEventListener("mousemove", this.mousemove);
  }
};
function zr(s99) {
  for (let t5 = s99; t5; t5 = t5.parentNode) if (t5.nodeType == 1 && t5.classList.contains("cm-tooltip")) return true;
  return false;
}
function Fr(s99, t5, e4, i9, n22, r2) {
  let o4 = document.createRange(), l11 = s99.domAtPos(t5), h3 = s99.domAtPos(e4);
  o4.setEnd(h3.node, h3.offset), o4.setStart(l11.node, l11.offset);
  let a2 = o4.getClientRects();
  o4.detach();
  for (let c4 = 0; c4 < a2.length; c4++) {
    let f2 = a2[c4];
    if (Math.max(f2.top - n22, n22 - f2.bottom, f2.left - i9, i9 - f2.right) <= r2) return true;
  }
  return false;
}
function lo(s99, t5 = {}) {
  let e4 = v.define(), i9 = $.define({
    create() {
      return null;
    },
    update(n22, r2) {
      if (n22 && (t5.hideOnChange && (r2.docChanged || r2.selection) || t5.hideOn && t5.hideOn(r2, n22))) return null;
      if (n22 && r2.docChanged) {
        let o4 = r2.changes.mapPos(n22.pos, -1, b.TrackDel);
        if (o4 == null) return null;
        let l11 = Object.assign(/* @__PURE__ */ Object.create(null), n22);
        l11.pos = o4, n22.end != null && (l11.end = r2.changes.mapPos(n22.end)), n22 = l11;
      }
      for (let o4 of r2.effects) o4.is(e4) && (n22 = o4.value), o4.is(on) && (n22 = null);
      return n22;
    },
    provide: (n22) => Pt.from(n22)
  });
  return [
    i9,
    P2.define((n22) => new ci(n22, s99, i9, e4, t5.hoverTime || 300)),
    Wr
  ];
}
function ho(s99, t5) {
  let e4 = s99.plugin(wi);
  if (!e4) return null;
  let i9 = e4.manager.tooltips.indexOf(t5);
  return i9 < 0 ? null : e4.manager.tooltipViews[i9];
}
var on = v.define();
var co = on.of(null);
var fi = y.define({
  combine(s99) {
    let t5, e4;
    for (let i9 of s99) t5 = t5 || i9.topContainer, e4 = e4 || i9.bottomContainer;
    return {
      topContainer: t5,
      bottomContainer: e4
    };
  }
});
function po(s99, t5) {
  let e4 = s99.plugin(ln), i9 = e4 ? e4.specs.indexOf(t5) : -1;
  return i9 > -1 ? e4.panels[i9] : null;
}
var ln = P2.fromClass(class {
  constructor(s99) {
    this.input = s99.state.facet(ns), this.specs = this.input.filter((e4) => e4), this.panels = this.specs.map((e4) => e4(s99));
    let t5 = s99.state.facet(fi);
    this.top = new ct(s99, true, t5.topContainer), this.bottom = new ct(s99, false, t5.bottomContainer), this.top.sync(this.panels.filter((e4) => e4.top)), this.bottom.sync(this.panels.filter((e4) => !e4.top));
    for (let e4 of this.panels) e4.dom.classList.add("cm-panel"), e4.mount && e4.mount();
  }
  update(s99) {
    let t5 = s99.state.facet(fi);
    this.top.container != t5.topContainer && (this.top.sync([]), this.top = new ct(s99.view, true, t5.topContainer)), this.bottom.container != t5.bottomContainer && (this.bottom.sync([]), this.bottom = new ct(s99.view, false, t5.bottomContainer)), this.top.syncClasses(), this.bottom.syncClasses();
    let e4 = s99.state.facet(ns);
    if (e4 != this.input) {
      let i9 = e4.filter((h3) => h3), n22 = [], r2 = [], o4 = [], l11 = [];
      for (let h3 of i9) {
        let a2 = this.specs.indexOf(h3), c4;
        a2 < 0 ? (c4 = h3(s99.view), l11.push(c4)) : (c4 = this.panels[a2], c4.update && c4.update(s99)), n22.push(c4), (c4.top ? r2 : o4).push(c4);
      }
      this.specs = i9, this.panels = n22, this.top.sync(r2), this.bottom.sync(o4);
      for (let h3 of l11) h3.dom.classList.add("cm-panel"), h3.mount && h3.mount();
    } else for (let i9 of this.panels) i9.update && i9.update(s99);
  }
  destroy() {
    this.top.sync([]), this.bottom.sync([]);
  }
}, {
  provide: (s99) => M2.scrollMargins.of((t5) => {
    let e4 = t5.plugin(s99);
    return e4 && {
      top: e4.top.scrollMargin(),
      bottom: e4.bottom.scrollMargin()
    };
  })
});
var ct = class {
  constructor(t5, e4, i9) {
    this.view = t5, this.top = e4, this.container = i9, this.dom = void 0, this.classes = "", this.panels = [], this.syncClasses();
  }
  sync(t5) {
    for (let e4 of this.panels) e4.destroy && t5.indexOf(e4) < 0 && e4.destroy();
    this.panels = t5, this.syncDOM();
  }
  syncDOM() {
    if (this.panels.length == 0) {
      this.dom && (this.dom.remove(), this.dom = void 0);
      return;
    }
    if (!this.dom) {
      this.dom = document.createElement("div"), this.dom.className = this.top ? "cm-panels cm-panels-top" : "cm-panels cm-panels-bottom", this.dom.style[this.top ? "top" : "bottom"] = "0";
      let e4 = this.container || this.view.dom;
      e4.insertBefore(this.dom, this.top ? e4.firstChild : null);
    }
    let t5 = this.dom.firstChild;
    for (let e4 of this.panels) if (e4.dom.parentNode == this.dom) {
      for (; t5 != e4.dom; ) t5 = ss(t5);
      t5 = t5.nextSibling;
    } else this.dom.insertBefore(e4.dom, t5);
    for (; t5; ) t5 = ss(t5);
  }
  scrollMargin() {
    return !this.dom || this.container ? 0 : Math.max(0, this.top ? this.dom.getBoundingClientRect().bottom - Math.max(0, this.view.scrollDOM.getBoundingClientRect().top) : Math.min(innerHeight, this.view.scrollDOM.getBoundingClientRect().bottom) - this.dom.getBoundingClientRect().top);
  }
  syncClasses() {
    if (!(!this.container || this.classes == this.view.themeClasses)) {
      for (let t5 of this.classes.split(" ")) t5 && this.container.classList.remove(t5);
      for (let t5 of (this.classes = this.view.themeClasses).split(" ")) t5 && this.container.classList.add(t5);
    }
  }
};
function ss(s99) {
  let t5 = s99.nextSibling;
  return s99.remove(), t5;
}
var ns = y.define({
  enables: ln
});
var I2 = class extends z {
  compare(t5) {
    return this == t5 || this.constructor == t5.constructor && this.eq(t5);
  }
  eq(t5) {
    return false;
  }
  destroy(t5) {
  }
};
I2.prototype.elementClass = "";
I2.prototype.toDOM = void 0;
I2.prototype.mapMode = b.TrackBefore;
I2.prototype.startSide = I2.prototype.endSide = -1;
I2.prototype.point = true;
var _t = y.define();
var Ir = {
  class: "",
  renderEmptyElements: false,
  elementStyle: "",
  markers: () => O.empty,
  lineMarker: () => null,
  lineMarkerChange: null,
  initialSpacer: null,
  updateSpacer: null,
  domEventHandlers: {}
};
var At = y.define();
function mo(s99) {
  return [
    hn(),
    At.of(Object.assign(Object.assign({}, Ir), s99))
  ];
}
var di = y.define({
  combine: (s99) => s99.some((t5) => t5)
});
function hn(s99) {
  let t5 = [
    qr
  ];
  return s99 && s99.fixed === false && t5.push(di.of(true)), t5;
}
var qr = P2.fromClass(class {
  constructor(s99) {
    this.view = s99, this.prevViewport = s99.viewport, this.dom = document.createElement("div"), this.dom.className = "cm-gutters", this.dom.setAttribute("aria-hidden", "true"), this.dom.style.minHeight = this.view.contentHeight + "px", this.gutters = s99.state.facet(At).map((t5) => new pe2(s99, t5));
    for (let t5 of this.gutters) this.dom.appendChild(t5.dom);
    this.fixed = !s99.state.facet(di), this.fixed && (this.dom.style.position = "sticky"), this.syncGutters(false), s99.scrollDOM.insertBefore(this.dom, s99.contentDOM);
  }
  update(s99) {
    if (this.updateGutters(s99)) {
      let t5 = this.prevViewport, e4 = s99.view.viewport, i9 = Math.min(t5.to, e4.to) - Math.max(t5.from, e4.from);
      this.syncGutters(i9 < (e4.to - e4.from) * 0.8);
    }
    s99.geometryChanged && (this.dom.style.minHeight = this.view.contentHeight + "px"), this.view.state.facet(di) != !this.fixed && (this.fixed = !this.fixed, this.dom.style.position = this.fixed ? "sticky" : ""), this.prevViewport = s99.view.viewport;
  }
  syncGutters(s99) {
    let t5 = this.dom.nextSibling;
    s99 && this.dom.remove();
    let e4 = O.iter(this.view.state.facet(_t), this.view.viewport.from), i9 = [], n22 = this.gutters.map((r2) => new ui(r2, this.view.viewport, -this.view.documentPadding.top));
    for (let r2 of this.view.viewportLineBlocks) {
      let o4;
      if (Array.isArray(r2.type)) {
        for (let l11 of r2.type) if (l11.type == D2.Text) {
          o4 = l11;
          break;
        }
      } else o4 = r2.type == D2.Text ? r2 : void 0;
      if (o4) {
        i9.length && (i9 = []), an(e4, i9, r2.from);
        for (let l11 of n22) l11.line(this.view, o4, i9);
      }
    }
    for (let r2 of n22) r2.finish();
    s99 && this.view.scrollDOM.insertBefore(this.dom, t5);
  }
  updateGutters(s99) {
    let t5 = s99.startState.facet(At), e4 = s99.state.facet(At), i9 = s99.docChanged || s99.heightChanged || s99.viewportChanged || !O.eq(s99.startState.facet(_t), s99.state.facet(_t), s99.view.viewport.from, s99.view.viewport.to);
    if (t5 == e4) for (let n22 of this.gutters) n22.update(s99) && (i9 = true);
    else {
      i9 = true;
      let n22 = [];
      for (let r2 of e4) {
        let o4 = t5.indexOf(r2);
        o4 < 0 ? n22.push(new pe2(this.view, r2)) : (this.gutters[o4].update(s99), n22.push(this.gutters[o4]));
      }
      for (let r2 of this.gutters) r2.dom.remove(), n22.indexOf(r2) < 0 && r2.destroy();
      for (let r2 of n22) this.dom.appendChild(r2.dom);
      this.gutters = n22;
    }
    return i9;
  }
  destroy() {
    for (let s99 of this.gutters) s99.destroy();
    this.dom.remove();
  }
}, {
  provide: (s99) => M2.scrollMargins.of((t5) => {
    let e4 = t5.plugin(s99);
    return !e4 || e4.gutters.length == 0 || !e4.fixed ? null : t5.textDirection == O2.LTR ? {
      left: e4.dom.offsetWidth
    } : {
      right: e4.dom.offsetWidth
    };
  })
});
function rs(s99) {
  return Array.isArray(s99) ? s99 : [
    s99
  ];
}
function an(s99, t5, e4) {
  for (; s99.value && s99.from <= e4; ) s99.from == e4 && t5.push(s99.value), s99.next();
}
var ui = class {
  constructor(t5, e4, i9) {
    this.gutter = t5, this.height = i9, this.localMarkers = [], this.i = 0, this.cursor = O.iter(t5.markers, e4.from);
  }
  line(t5, e4, i9) {
    this.localMarkers.length && (this.localMarkers = []), an(this.cursor, this.localMarkers, e4.from);
    let n22 = i9.length ? this.localMarkers.concat(i9) : this.localMarkers, r2 = this.gutter.config.lineMarker(t5, e4, n22);
    r2 && n22.unshift(r2);
    let o4 = this.gutter;
    if (n22.length == 0 && !o4.config.renderEmptyElements) return;
    let l11 = e4.top - this.height;
    if (this.i == o4.elements.length) {
      let h3 = new me2(t5, e4.height, l11, n22);
      o4.elements.push(h3), o4.dom.appendChild(h3.dom);
    } else o4.elements[this.i].update(t5, e4.height, l11, n22);
    this.height = e4.bottom, this.i++;
  }
  finish() {
    let t5 = this.gutter;
    for (; t5.elements.length > this.i; ) {
      let e4 = t5.elements.pop();
      t5.dom.removeChild(e4.dom), e4.destroy();
    }
  }
};
var pe2 = class {
  constructor(t5, e4) {
    this.view = t5, this.config = e4, this.elements = [], this.spacer = null, this.dom = document.createElement("div"), this.dom.className = "cm-gutter" + (this.config.class ? " " + this.config.class : "");
    for (let i9 in e4.domEventHandlers) this.dom.addEventListener(i9, (n22) => {
      let r2 = t5.lineBlockAtHeight(n22.clientY - t5.documentTop);
      e4.domEventHandlers[i9](t5, r2, n22) && n22.preventDefault();
    });
    this.markers = rs(e4.markers(t5)), e4.initialSpacer && (this.spacer = new me2(t5, 0, 0, [
      e4.initialSpacer(t5)
    ]), this.dom.appendChild(this.spacer.dom), this.spacer.dom.style.cssText += "visibility: hidden; pointer-events: none");
  }
  update(t5) {
    let e4 = this.markers;
    if (this.markers = rs(this.config.markers(t5.view)), this.spacer && this.config.updateSpacer) {
      let n22 = this.config.updateSpacer(this.spacer.markers[0], t5);
      n22 != this.spacer.markers[0] && this.spacer.update(t5.view, 0, 0, [
        n22
      ]);
    }
    let i9 = t5.view.viewport;
    return !O.eq(this.markers, e4, i9.from, i9.to) || (this.config.lineMarkerChange ? this.config.lineMarkerChange(t5) : false);
  }
  destroy() {
    for (let t5 of this.elements) t5.destroy();
  }
};
var me2 = class {
  constructor(t5, e4, i9, n22) {
    this.height = -1, this.above = 0, this.markers = [], this.dom = document.createElement("div"), this.dom.className = "cm-gutterElement", this.update(t5, e4, i9, n22);
  }
  update(t5, e4, i9, n22) {
    this.height != e4 && (this.dom.style.height = (this.height = e4) + "px"), this.above != i9 && (this.dom.style.marginTop = (this.above = i9) ? i9 + "px" : ""), Kr(this.markers, n22) || this.setMarkers(t5, n22);
  }
  setMarkers(t5, e4) {
    let i9 = "cm-gutterElement", n22 = this.dom.firstChild;
    for (let r2 = 0, o4 = 0; ; ) {
      let l11 = o4, h3 = r2 < e4.length ? e4[r2++] : null, a2 = false;
      if (h3) {
        let c4 = h3.elementClass;
        c4 && (i9 += " " + c4);
        for (let f2 = o4; f2 < this.markers.length; f2++) if (this.markers[f2].compare(h3)) {
          l11 = f2, a2 = true;
          break;
        }
      } else l11 = this.markers.length;
      for (; o4 < l11; ) {
        let c4 = this.markers[o4++];
        if (c4.toDOM) {
          c4.destroy(n22);
          let f2 = n22.nextSibling;
          n22.remove(), n22 = f2;
        }
      }
      if (!h3) break;
      h3.toDOM && (a2 ? n22 = n22.nextSibling : this.dom.insertBefore(h3.toDOM(t5), n22)), a2 && o4++;
    }
    this.dom.className = i9, this.markers = e4;
  }
  destroy() {
    this.setMarkers(null, []);
  }
};
function Kr(s99, t5) {
  if (s99.length != t5.length) return false;
  for (let e4 = 0; e4 < s99.length; e4++) if (!s99[e4].compare(t5[e4])) return false;
  return true;
}
var jr = y.define();
var ft = y.define({
  combine(s99) {
    return ht(s99, {
      formatNumber: String,
      domEventHandlers: {}
    }, {
      domEventHandlers(t5, e4) {
        let i9 = Object.assign({}, t5);
        for (let n22 in e4) {
          let r2 = i9[n22], o4 = e4[n22];
          i9[n22] = r2 ? (l11, h3, a2) => r2(l11, h3, a2) || o4(l11, h3, a2) : o4;
        }
        return i9;
      }
    });
  }
});
var Dt = class extends I2 {
  constructor(t5) {
    super(), this.number = t5;
  }
  eq(t5) {
    return this.number == t5.number;
  }
  toDOM() {
    return document.createTextNode(this.number);
  }
};
function ke2(s99, t5) {
  return s99.state.facet(ft).formatNumber(t5, s99.state);
}
var Gr = At.compute([
  ft
], (s99) => ({
  class: "cm-lineNumbers",
  renderEmptyElements: false,
  markers(t5) {
    return t5.state.facet(jr);
  },
  lineMarker(t5, e4, i9) {
    return i9.some((n22) => n22.toDOM) ? null : new Dt(ke2(t5, t5.state.doc.lineAt(e4.from).number));
  },
  lineMarkerChange: (t5) => t5.startState.facet(ft) != t5.state.facet(ft),
  initialSpacer(t5) {
    return new Dt(ke2(t5, os(t5.state.doc.lines)));
  },
  updateSpacer(t5, e4) {
    let i9 = ke2(e4.view, os(e4.view.state.doc.lines));
    return i9 == t5.number ? t5 : new Dt(i9);
  },
  domEventHandlers: s99.facet(ft).domEventHandlers
}));
function go(s99 = {}) {
  return [
    ft.of(s99),
    hn(),
    Gr
  ];
}
function os(s99) {
  let t5 = 9;
  for (; t5 < s99; ) t5 = t5 * 10 + 9;
  return t5;
}
var $r = new class extends I2 {
  constructor() {
    super(...arguments), this.elementClass = "cm-activeLineGutter";
  }
}();
var _r = _t.compute([
  "selection"
], (s99) => {
  let t5 = [], e4 = -1;
  for (let i9 of s99.selection.ranges) if (i9.empty) {
    let n22 = s99.doc.lineAt(i9.head).from;
    n22 > e4 && (e4 = n22, t5.push($r.range(n22)));
  }
  return O.of(t5);
});
function bo() {
  return _r;
}

// deno:https://esm.sh/@lezer/common@0.16.1/denonext/common.mjs
var Ce3 = 0;
var N3 = class {
  constructor(e4, t5) {
    this.from = e4, this.to = t5;
  }
};
var w3 = class {
  constructor(e4 = {}) {
    this.id = Ce3++, this.perNode = !!e4.perNode, this.deserialize = e4.deserialize || (() => {
      throw new Error("This node type doesn't define a deserialize function");
    });
  }
  add(e4) {
    if (this.perNode) throw new RangeError("Can't add per-node props to node types");
    return typeof e4 != "function" && (e4 = T4.match(e4)), (t5) => {
      let r2 = e4(t5);
      return r2 === void 0 ? null : [
        this,
        r2
      ];
    };
  }
};
w3.closedBy = new w3({
  deserialize: (l11) => l11.split(" ")
});
w3.openedBy = new w3({
  deserialize: (l11) => l11.split(" ")
});
w3.group = new w3({
  deserialize: (l11) => l11.split(" ")
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
  constructor(e4, t5, r2, i9 = 0) {
    this.name = e4, this.props = t5, this.id = r2, this.flags = i9;
  }
  static define(e4) {
    let t5 = e4.props && e4.props.length ? /* @__PURE__ */ Object.create(null) : _e3, r2 = (e4.top ? 1 : 0) | (e4.skipped ? 2 : 0) | (e4.error ? 4 : 0) | (e4.name == null ? 8 : 0), i9 = new l(e4.name || "", t5, e4.id, r2);
    if (e4.props) {
      for (let n22 of e4.props) if (Array.isArray(n22) || (n22 = n22(i9)), n22) {
        if (n22[0].perNode) throw new RangeError("Can't store a per-node prop on a node type");
        t5[n22[0].id] = n22[1];
      }
    }
    return i9;
  }
  prop(e4) {
    return this.props[e4.id];
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
  is(e4) {
    if (typeof e4 == "string") {
      if (this.name == e4) return true;
      let t5 = this.prop(w3.group);
      return t5 ? t5.indexOf(e4) > -1 : false;
    }
    return this.id == e4;
  }
  static match(e4) {
    let t5 = /* @__PURE__ */ Object.create(null);
    for (let r2 in e4) for (let i9 of r2.split(" ")) t5[i9] = e4[r2];
    return (r2) => {
      for (let i9 = r2.prop(w3.group), n22 = -1; n22 < (i9 ? i9.length : 0); n22++) {
        let s99 = t5[n22 < 0 ? r2.name : i9[n22]];
        if (s99) return s99;
      }
    };
  }
};
T4.none = new T4("", /* @__PURE__ */ Object.create(null), 0, 8);
var ce3 = class l2 {
  constructor(e4) {
    this.types = e4;
    for (let t5 = 0; t5 < e4.length; t5++) if (e4[t5].id != t5) throw new RangeError("Node type ids should correspond to array positions when creating a node set");
  }
  extend(...e4) {
    let t5 = [];
    for (let r2 of this.types) {
      let i9 = null;
      for (let n22 of e4) {
        let s99 = n22(r2);
        s99 && (i9 || (i9 = Object.assign({}, r2.props)), i9[s99[0].id] = s99[1]);
      }
      t5.push(i9 ? new T4(r2.name, i9, r2.id, r2.flags) : r2);
    }
    return new l2(t5);
  }
};
var K3 = /* @__PURE__ */ new WeakMap();
var ge3 = /* @__PURE__ */ new WeakMap();
var A2;
(function(l11) {
  l11[l11.ExcludeBuffers = 1] = "ExcludeBuffers", l11[l11.IncludeAnonymous = 2] = "IncludeAnonymous", l11[l11.IgnoreMounts = 4] = "IgnoreMounts", l11[l11.IgnoreOverlays = 8] = "IgnoreOverlays";
})(A2 || (A2 = {}));
var z3 = class l3 {
  constructor(e4, t5, r2, i9, n22) {
    if (this.type = e4, this.children = t5, this.positions = r2, this.length = i9, this.props = null, n22 && n22.length) {
      this.props = /* @__PURE__ */ Object.create(null);
      for (let [s99, h3] of n22) this.props[typeof s99 == "number" ? s99 : s99.id] = h3;
    }
  }
  toString() {
    let e4 = this.prop(w3.mounted);
    if (e4 && !e4.overlay) return e4.tree.toString();
    let t5 = "";
    for (let r2 of this.children) {
      let i9 = r2.toString();
      i9 && (t5 && (t5 += ","), t5 += i9);
    }
    return this.type.name ? (/\W/.test(this.type.name) && !this.type.isError ? JSON.stringify(this.type.name) : this.type.name) + (t5.length ? "(" + t5 + ")" : "") : t5;
  }
  cursor(e4 = 0) {
    return new V3(this.topNode, e4);
  }
  cursorAt(e4, t5 = 0, r2 = 0) {
    let i9 = K3.get(this) || this.topNode, n22 = new V3(i9);
    return n22.moveTo(e4, t5), K3.set(this, n22._tree), n22;
  }
  get topNode() {
    return new M3(this, 0, 0, null);
  }
  resolve(e4, t5 = 0) {
    let r2 = $2(K3.get(this) || this.topNode, e4, t5, false);
    return K3.set(this, r2), r2;
  }
  resolveInner(e4, t5 = 0) {
    let r2 = $2(ge3.get(this) || this.topNode, e4, t5, true);
    return ge3.set(this, r2), r2;
  }
  iterate(e4) {
    let { enter: t5, leave: r2, from: i9 = 0, to: n22 = this.length } = e4;
    for (let s99 = this.cursor((e4.mode || 0) | A2.IncludeAnonymous); ; ) {
      let h3 = false;
      if (s99.from <= n22 && s99.to >= i9 && (s99.type.isAnonymous || t5(s99) !== false)) {
        if (s99.firstChild()) continue;
        h3 = true;
      }
      for (; h3 && r2 && !s99.type.isAnonymous && r2(s99), !s99.nextSibling(); ) {
        if (!s99.parent()) return;
        h3 = true;
      }
    }
  }
  prop(e4) {
    return e4.perNode ? this.props ? this.props[e4.id] : void 0 : this.type.prop(e4);
  }
  get propValues() {
    let e4 = [];
    if (this.props) for (let t5 in this.props) e4.push([
      +t5,
      this.props[t5]
    ]);
    return e4;
  }
  balance(e4 = {}) {
    return this.children.length <= 8 ? this : ae3(T4.none, this.children, this.positions, 0, this.children.length, 0, this.length, (t5, r2, i9) => new l3(this.type, t5, r2, i9, this.propValues), e4.makeTree || ((t5, r2, i9) => new l3(T4.none, t5, r2, i9)));
  }
  static build(e4) {
    return Se3(e4);
  }
};
z3.empty = new z3(T4.none, [], [], 0);
var ie3 = class l4 {
  constructor(e4, t5) {
    this.buffer = e4, this.index = t5;
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
  constructor(e4, t5, r2) {
    this.buffer = e4, this.length = t5, this.set = r2;
  }
  get type() {
    return T4.none;
  }
  toString() {
    let e4 = [];
    for (let t5 = 0; t5 < this.buffer.length; ) e4.push(this.childString(t5)), t5 = this.buffer[t5 + 3];
    return e4.join(",");
  }
  childString(e4) {
    let t5 = this.buffer[e4], r2 = this.buffer[e4 + 3], i9 = this.set.types[t5], n22 = i9.name;
    if (/\W/.test(n22) && !i9.isError && (n22 = JSON.stringify(n22)), e4 += 4, r2 == e4) return n22;
    let s99 = [];
    for (; e4 < r2; ) s99.push(this.childString(e4)), e4 = this.buffer[e4 + 3];
    return n22 + "(" + s99.join(",") + ")";
  }
  findChild(e4, t5, r2, i9, n22) {
    let { buffer: s99 } = this, h3 = -1;
    for (let f2 = e4; f2 != t5 && !(ke3(n22, i9, s99[f2 + 1], s99[f2 + 2]) && (h3 = f2, r2 > 0)); f2 = s99[f2 + 3]) ;
    return h3;
  }
  slice(e4, t5, r2, i9) {
    let n22 = this.buffer, s99 = new Uint16Array(t5 - e4);
    for (let h3 = e4, f2 = 0; h3 < t5; ) s99[f2++] = n22[h3++], s99[f2++] = n22[h3++] - r2, s99[f2++] = n22[h3++] - r2, s99[f2++] = n22[h3++] - e4;
    return new l5(s99, i9 - r2, this.set);
  }
};
function ke3(l11, e4, t5, r2) {
  switch (l11) {
    case -2:
      return t5 < e4;
    case -1:
      return r2 >= e4 && t5 < e4;
    case 0:
      return t5 < e4 && r2 > e4;
    case 1:
      return t5 <= e4 && r2 > e4;
    case 2:
      return r2 > e4;
    case 4:
      return true;
  }
}
function Ae2(l11, e4) {
  let t5 = l11.childBefore(e4);
  for (; t5; ) {
    let r2 = t5.lastChild;
    if (!r2 || r2.to != t5.to) break;
    r2.type.isError && r2.from == r2.to ? (l11 = t5, t5 = r2.prevSibling) : t5 = r2;
  }
  return l11;
}
function $2(l11, e4, t5, r2) {
  for (var i9; l11.from == l11.to || (t5 < 1 ? l11.from >= e4 : l11.from > e4) || (t5 > -1 ? l11.to <= e4 : l11.to < e4); ) {
    let s99 = !r2 && l11 instanceof M3 && l11.index < 0 ? null : l11.parent;
    if (!s99) return l11;
    l11 = s99;
  }
  let n22 = r2 ? 0 : A2.IgnoreOverlays;
  if (r2) for (let s99 = l11, h3 = s99.parent; h3; s99 = h3, h3 = s99.parent) s99 instanceof M3 && s99.index < 0 && ((i9 = h3.enter(e4, t5, n22)) === null || i9 === void 0 ? void 0 : i9.from) != s99.from && (l11 = h3);
  for (; ; ) {
    let s99 = l11.enter(e4, t5, n22);
    if (!s99) return l11;
    l11 = s99;
  }
}
var M3 = class l6 {
  constructor(e4, t5, r2, i9) {
    this._tree = e4, this.from = t5, this.index = r2, this._parent = i9;
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
  nextChild(e4, t5, r2, i9, n22 = 0) {
    for (let s99 = this; ; ) {
      for (let { children: h3, positions: f2 } = s99._tree, u5 = t5 > 0 ? h3.length : -1; e4 != u5; e4 += t5) {
        let o4 = h3[e4], d5 = f2[e4] + s99.from;
        if (ke3(i9, r2, d5, d5 + o4.length)) {
          if (o4 instanceof W3) {
            if (n22 & A2.ExcludeBuffers) continue;
            let a2 = o4.findChild(0, o4.buffer.length, t5, r2 - d5, i9);
            if (a2 > -1) return new H2(new ne3(s99, o4, e4, d5), null, a2);
          } else if (n22 & A2.IncludeAnonymous || !o4.type.isAnonymous || ue3(o4)) {
            let a2;
            if (!(n22 & A2.IgnoreMounts) && o4.props && (a2 = o4.prop(w3.mounted)) && !a2.overlay) return new l6(a2.tree, d5, e4, s99);
            let y10 = new l6(o4, d5, e4, s99);
            return n22 & A2.IncludeAnonymous || !y10.type.isAnonymous ? y10 : y10.nextChild(t5 < 0 ? o4.children.length - 1 : 0, t5, r2, i9);
          }
        }
      }
      if (n22 & A2.IncludeAnonymous || !s99.type.isAnonymous || (s99.index >= 0 ? e4 = s99.index + t5 : e4 = t5 < 0 ? -1 : s99._parent._tree.children.length, s99 = s99._parent, !s99)) return null;
    }
  }
  get firstChild() {
    return this.nextChild(0, 1, 0, 4);
  }
  get lastChild() {
    return this.nextChild(this._tree.children.length - 1, -1, 0, 4);
  }
  childAfter(e4) {
    return this.nextChild(0, 1, e4, 2);
  }
  childBefore(e4) {
    return this.nextChild(this._tree.children.length - 1, -1, e4, -2);
  }
  enter(e4, t5, r2 = 0) {
    let i9;
    if (!(r2 & A2.IgnoreOverlays) && (i9 = this._tree.prop(w3.mounted)) && i9.overlay) {
      let n22 = e4 - this.from;
      for (let { from: s99, to: h3 } of i9.overlay) if ((t5 > 0 ? s99 <= n22 : s99 < n22) && (t5 < 0 ? h3 >= n22 : h3 > n22)) return new l6(i9.tree, i9.overlay[0].from + this.from, -1, this);
    }
    return this.nextChild(0, 1, e4, t5, r2);
  }
  nextSignificantParent() {
    let e4 = this;
    for (; e4.type.isAnonymous && e4._parent; ) e4 = e4._parent;
    return e4;
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
  cursor(e4 = 0) {
    return new V3(this, e4);
  }
  get tree() {
    return this._tree;
  }
  toTree() {
    return this._tree;
  }
  resolve(e4, t5 = 0) {
    return $2(this, e4, t5, false);
  }
  resolveInner(e4, t5 = 0) {
    return $2(this, e4, t5, true);
  }
  enterUnfinishedNodesBefore(e4) {
    return Ae2(this, e4);
  }
  getChild(e4, t5 = null, r2 = null) {
    let i9 = X3(this, e4, t5, r2);
    return i9.length ? i9[0] : null;
  }
  getChildren(e4, t5 = null, r2 = null) {
    return X3(this, e4, t5, r2);
  }
  toString() {
    return this._tree.toString();
  }
  get node() {
    return this;
  }
  matchContext(e4) {
    return Y2(this, e4);
  }
};
function X3(l11, e4, t5, r2) {
  let i9 = l11.cursor(), n22 = [];
  if (!i9.firstChild()) return n22;
  if (t5 != null) {
    for (; !i9.type.is(t5); ) if (!i9.nextSibling()) return n22;
  }
  for (; ; ) {
    if (r2 != null && i9.type.is(r2)) return n22;
    if (i9.type.is(e4) && n22.push(i9.node), !i9.nextSibling()) return r2 == null ? n22 : [];
  }
}
function Y2(l11, e4, t5 = e4.length - 1) {
  for (let r2 = l11.parent; t5 >= 0; r2 = r2.parent) {
    if (!r2) return false;
    if (!r2.type.isAnonymous) {
      if (e4[t5] && e4[t5] != r2.name) return false;
      t5--;
    }
  }
  return true;
}
var ne3 = class {
  constructor(e4, t5, r2, i9) {
    this.parent = e4, this.buffer = t5, this.index = r2, this.start = i9;
  }
};
var H2 = class l7 {
  constructor(e4, t5, r2) {
    this.context = e4, this._parent = t5, this.index = r2, this.type = e4.buffer.set.types[e4.buffer.buffer[r2]];
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
  child(e4, t5, r2) {
    let { buffer: i9 } = this.context, n22 = i9.findChild(this.index + 4, i9.buffer[this.index + 3], e4, t5 - this.context.start, r2);
    return n22 < 0 ? null : new l7(this.context, this, n22);
  }
  get firstChild() {
    return this.child(1, 0, 4);
  }
  get lastChild() {
    return this.child(-1, 0, 4);
  }
  childAfter(e4) {
    return this.child(1, e4, 2);
  }
  childBefore(e4) {
    return this.child(-1, e4, -2);
  }
  enter(e4, t5, r2 = 0) {
    if (r2 & A2.ExcludeBuffers) return null;
    let { buffer: i9 } = this.context, n22 = i9.findChild(this.index + 4, i9.buffer[this.index + 3], t5 > 0 ? 1 : -1, e4 - this.context.start, t5);
    return n22 < 0 ? null : new l7(this.context, this, n22);
  }
  get parent() {
    return this._parent || this.context.parent.nextSignificantParent();
  }
  externalSibling(e4) {
    return this._parent ? null : this.context.parent.nextChild(this.context.index + e4, e4, 0, 4);
  }
  get nextSibling() {
    let { buffer: e4 } = this.context, t5 = e4.buffer[this.index + 3];
    return t5 < (this._parent ? e4.buffer[this._parent.index + 3] : e4.buffer.length) ? new l7(this.context, this._parent, t5) : this.externalSibling(1);
  }
  get prevSibling() {
    let { buffer: e4 } = this.context, t5 = this._parent ? this._parent.index + 4 : 0;
    return this.index == t5 ? this.externalSibling(-1) : new l7(this.context, this._parent, e4.findChild(t5, this.index, -1, 0, 4));
  }
  cursor(e4 = 0) {
    return new V3(this, e4);
  }
  get tree() {
    return null;
  }
  toTree() {
    let e4 = [], t5 = [], { buffer: r2 } = this.context, i9 = this.index + 4, n22 = r2.buffer[this.index + 3];
    if (n22 > i9) {
      let s99 = r2.buffer[this.index + 1], h3 = r2.buffer[this.index + 2];
      e4.push(r2.slice(i9, n22, s99, h3)), t5.push(0);
    }
    return new z3(this.type, e4, t5, this.to - this.from);
  }
  resolve(e4, t5 = 0) {
    return $2(this, e4, t5, false);
  }
  resolveInner(e4, t5 = 0) {
    return $2(this, e4, t5, true);
  }
  enterUnfinishedNodesBefore(e4) {
    return Ae2(this, e4);
  }
  toString() {
    return this.context.buffer.childString(this.index);
  }
  getChild(e4, t5 = null, r2 = null) {
    let i9 = X3(this, e4, t5, r2);
    return i9.length ? i9[0] : null;
  }
  getChildren(e4, t5 = null, r2 = null) {
    return X3(this, e4, t5, r2);
  }
  get node() {
    return this;
  }
  matchContext(e4) {
    return Y2(this, e4);
  }
};
var V3 = class {
  constructor(e4, t5 = 0) {
    if (this.mode = t5, this.buffer = null, this.stack = [], this.index = 0, this.bufferNode = null, e4 instanceof M3) this.yieldNode(e4);
    else {
      this._tree = e4.context.parent, this.buffer = e4.context;
      for (let r2 = e4._parent; r2; r2 = r2._parent) this.stack.unshift(r2.index);
      this.bufferNode = e4, this.yieldBuf(e4.index);
    }
  }
  get name() {
    return this.type.name;
  }
  yieldNode(e4) {
    return e4 ? (this._tree = e4, this.type = e4.type, this.from = e4.from, this.to = e4.to, true) : false;
  }
  yieldBuf(e4, t5) {
    this.index = e4;
    let { start: r2, buffer: i9 } = this.buffer;
    return this.type = t5 || i9.set.types[i9.buffer[e4]], this.from = r2 + i9.buffer[e4 + 1], this.to = r2 + i9.buffer[e4 + 2], true;
  }
  yield(e4) {
    return e4 ? e4 instanceof M3 ? (this.buffer = null, this.yieldNode(e4)) : (this.buffer = e4.context, this.yieldBuf(e4.index, e4.type)) : false;
  }
  toString() {
    return this.buffer ? this.buffer.buffer.childString(this.index) : this._tree.toString();
  }
  enterChild(e4, t5, r2) {
    if (!this.buffer) return this.yield(this._tree.nextChild(e4 < 0 ? this._tree._tree.children.length - 1 : 0, e4, t5, r2, this.mode));
    let { buffer: i9 } = this.buffer, n22 = i9.findChild(this.index + 4, i9.buffer[this.index + 3], e4, t5 - this.buffer.start, r2);
    return n22 < 0 ? false : (this.stack.push(this.index), this.yieldBuf(n22));
  }
  firstChild() {
    return this.enterChild(1, 0, 4);
  }
  lastChild() {
    return this.enterChild(-1, 0, 4);
  }
  childAfter(e4) {
    return this.enterChild(1, e4, 2);
  }
  childBefore(e4) {
    return this.enterChild(-1, e4, -2);
  }
  enter(e4, t5, r2 = this.mode) {
    return this.buffer ? r2 & A2.ExcludeBuffers ? false : this.enterChild(1, e4, t5) : this.yield(this._tree.enter(e4, t5, r2));
  }
  parent() {
    if (!this.buffer) return this.yieldNode(this.mode & A2.IncludeAnonymous ? this._tree._parent : this._tree.parent);
    if (this.stack.length) return this.yieldBuf(this.stack.pop());
    let e4 = this.mode & A2.IncludeAnonymous ? this.buffer.parent : this.buffer.parent.nextSignificantParent();
    return this.buffer = null, this.yieldNode(e4);
  }
  sibling(e4) {
    if (!this.buffer) return this._tree._parent ? this.yield(this._tree.index < 0 ? null : this._tree._parent.nextChild(this._tree.index + e4, e4, 0, 4, this.mode)) : false;
    let { buffer: t5 } = this.buffer, r2 = this.stack.length - 1;
    if (e4 < 0) {
      let i9 = r2 < 0 ? 0 : this.stack[r2] + 4;
      if (this.index != i9) return this.yieldBuf(t5.findChild(i9, this.index, -1, 0, 4));
    } else {
      let i9 = t5.buffer[this.index + 3];
      if (i9 < (r2 < 0 ? t5.buffer.length : t5.buffer[this.stack[r2] + 3])) return this.yieldBuf(i9);
    }
    return r2 < 0 ? this.yield(this.buffer.parent.nextChild(this.buffer.index + e4, e4, 0, 4, this.mode)) : false;
  }
  nextSibling() {
    return this.sibling(1);
  }
  prevSibling() {
    return this.sibling(-1);
  }
  atLastNode(e4) {
    let t5, r2, { buffer: i9 } = this;
    if (i9) {
      if (e4 > 0) {
        if (this.index < i9.buffer.buffer.length) return false;
      } else for (let n22 = 0; n22 < this.index; n22++) if (i9.buffer.buffer[n22 + 3] < this.index) return false;
      ({ index: t5, parent: r2 } = i9);
    } else ({ index: t5, _parent: r2 } = this._tree);
    for (; r2; { index: t5, _parent: r2 } = r2) if (t5 > -1) for (let n22 = t5 + e4, s99 = e4 < 0 ? -1 : r2._tree.children.length; n22 != s99; n22 += e4) {
      let h3 = r2._tree.children[n22];
      if (this.mode & A2.IncludeAnonymous || h3 instanceof W3 || !h3.type.isAnonymous || ue3(h3)) return false;
    }
    return true;
  }
  move(e4, t5) {
    if (t5 && this.enterChild(e4, 0, 4)) return true;
    for (; ; ) {
      if (this.sibling(e4)) return true;
      if (this.atLastNode(e4) || !this.parent()) return false;
    }
  }
  next(e4 = true) {
    return this.move(1, e4);
  }
  prev(e4 = true) {
    return this.move(-1, e4);
  }
  moveTo(e4, t5 = 0) {
    for (; (this.from == this.to || (t5 < 1 ? this.from >= e4 : this.from > e4) || (t5 > -1 ? this.to <= e4 : this.to < e4)) && this.parent(); ) ;
    for (; this.enterChild(1, e4, t5); ) ;
    return this;
  }
  get node() {
    if (!this.buffer) return this._tree;
    let e4 = this.bufferNode, t5 = null, r2 = 0;
    if (e4 && e4.context == this.buffer) e: for (let i9 = this.index, n22 = this.stack.length; n22 >= 0; ) {
      for (let s99 = e4; s99; s99 = s99._parent) if (s99.index == i9) {
        if (i9 == this.index) return s99;
        t5 = s99, r2 = n22 + 1;
        break e;
      }
      i9 = this.stack[--n22];
    }
    for (let i9 = r2; i9 < this.stack.length; i9++) t5 = new H2(this.buffer, t5, this.stack[i9]);
    return this.bufferNode = new H2(this.buffer, t5, this.index);
  }
  get tree() {
    return this.buffer ? null : this._tree._tree;
  }
  iterate(e4, t5) {
    for (let r2 = 0; ; ) {
      let i9 = false;
      if (this.type.isAnonymous || e4(this) !== false) {
        if (this.firstChild()) {
          r2++;
          continue;
        }
        this.type.isAnonymous || (i9 = true);
      }
      for (; i9 && t5 && t5(this), i9 = this.type.isAnonymous, !this.nextSibling(); ) {
        if (!r2) return;
        this.parent(), r2--, i9 = true;
      }
    }
  }
  matchContext(e4) {
    if (!this.buffer) return Y2(this.node, e4);
    let { buffer: t5 } = this.buffer, { types: r2 } = t5.set;
    for (let i9 = e4.length - 1, n22 = this.stack.length - 1; i9 >= 0; n22--) {
      if (n22 < 0) return Y2(this.node, e4, i9);
      let s99 = r2[t5.buffer[this.stack[n22]]];
      if (!s99.isAnonymous) {
        if (e4[i9] && e4[i9] != s99.name) return false;
        i9--;
      }
    }
    return true;
  }
};
function ue3(l11) {
  return l11.children.some((e4) => e4 instanceof W3 || !e4.type.isAnonymous || ue3(e4));
}
function Se3(l11) {
  var e4;
  let { buffer: t5, nodeSet: r2, maxBufferLength: i9 = 1024, reused: n22 = [], minRepeatType: s99 = r2.types.length } = l11, h3 = Array.isArray(t5) ? new ie3(t5, t5.length) : t5, f2 = r2.types, u5 = 0, o4 = 0;
  function d5(x11, v8, p5, m9, C12) {
    let { id: b9, start: g6, end: k13, size: B13 } = h3, I13 = o4;
    for (; B13 < 0; ) if (h3.next(), B13 == -1) {
      let R12 = n22[b9];
      p5.push(R12), m9.push(g6 - x11);
      return;
    } else if (B13 == -3) {
      u5 = b9;
      return;
    } else if (B13 == -4) {
      o4 = b9;
      return;
    } else throw new RangeError(`Unrecognized record size: ${B13}`);
    let G12 = f2[b9], L10, F13, pe10 = g6 - x11;
    if (k13 - g6 <= i9 && (F13 = S11(h3.pos - v8, C12))) {
      let R12 = new Uint16Array(F13.size - F13.skip), E12 = h3.pos - F13.size, D9 = R12.length;
      for (; h3.pos > E12; ) D9 = O9(F13.start, R12, D9);
      L10 = new W3(R12, k13 - F13.start, r2), pe10 = F13.start - x11;
    } else {
      let R12 = h3.pos - B13;
      h3.next();
      let E12 = [], D9 = [], U14 = b9 >= s99 ? b9 : -1, J8 = 0, q13 = k13;
      for (; h3.pos > R12; ) U14 >= 0 && h3.id == U14 && h3.size >= 0 ? (h3.end <= q13 - i9 && (y10(E12, D9, g6, J8, h3.end, q13, U14, I13), J8 = E12.length, q13 = h3.end), h3.next()) : d5(g6, R12, E12, D9, U14);
      if (U14 >= 0 && J8 > 0 && J8 < E12.length && y10(E12, D9, g6, J8, g6, q13, U14, I13), E12.reverse(), D9.reverse(), U14 > -1 && J8 > 0) {
        let de13 = a2(G12);
        L10 = ae3(G12, E12, D9, 0, E12.length, 0, k13 - g6, de13, de13);
      } else L10 = c4(G12, E12, D9, k13 - g6, I13 - k13);
    }
    p5.push(L10), m9.push(pe10);
  }
  function a2(x11) {
    return (v8, p5, m9) => {
      let C12 = 0, b9 = v8.length - 1, g6, k13;
      if (b9 >= 0 && (g6 = v8[b9]) instanceof z3) {
        if (!b9 && g6.type == x11 && g6.length == m9) return g6;
        (k13 = g6.prop(w3.lookAhead)) && (C12 = p5[b9] + g6.length + k13);
      }
      return c4(x11, v8, p5, m9, C12);
    };
  }
  function y10(x11, v8, p5, m9, C12, b9, g6, k13) {
    let B13 = [], I13 = [];
    for (; x11.length > m9; ) B13.push(x11.pop()), I13.push(v8.pop() + p5 - C12);
    x11.push(c4(r2.types[g6], B13, I13, b9 - C12, k13 - b9)), v8.push(C12 - p5);
  }
  function c4(x11, v8, p5, m9, C12 = 0, b9) {
    if (u5) {
      let g6 = [
        w3.contextHash,
        u5
      ];
      b9 = b9 ? [
        g6
      ].concat(b9) : [
        g6
      ];
    }
    if (C12 > 25) {
      let g6 = [
        w3.lookAhead,
        C12
      ];
      b9 = b9 ? [
        g6
      ].concat(b9) : [
        g6
      ];
    }
    return new z3(x11, v8, p5, m9, b9);
  }
  function S11(x11, v8) {
    let p5 = h3.fork(), m9 = 0, C12 = 0, b9 = 0, g6 = p5.end - i9, k13 = {
      size: 0,
      start: 0,
      skip: 0
    };
    e: for (let B13 = p5.pos - x11; p5.pos > B13; ) {
      let I13 = p5.size;
      if (p5.id == v8 && I13 >= 0) {
        k13.size = m9, k13.start = C12, k13.skip = b9, b9 += 4, m9 += 4, p5.next();
        continue;
      }
      let G12 = p5.pos - I13;
      if (I13 < 0 || G12 < B13 || p5.start < g6) break;
      let L10 = p5.id >= s99 ? 4 : 0, F13 = p5.start;
      for (p5.next(); p5.pos > G12; ) {
        if (p5.size < 0) if (p5.size == -3) L10 += 4;
        else break e;
        else p5.id >= s99 && (L10 += 4);
        p5.next();
      }
      C12 = F13, m9 += I13, b9 += L10;
    }
    return (v8 < 0 || m9 == x11) && (k13.size = m9, k13.start = C12, k13.skip = b9), k13.size > 4 ? k13 : void 0;
  }
  function O9(x11, v8, p5) {
    let { id: m9, start: C12, end: b9, size: g6 } = h3;
    if (h3.next(), g6 >= 0 && m9 < s99) {
      let k13 = p5;
      if (g6 > 4) {
        let B13 = h3.pos - (g6 - 4);
        for (; h3.pos > B13; ) p5 = O9(x11, v8, p5);
      }
      v8[--p5] = k13, v8[--p5] = b9 - x11, v8[--p5] = C12 - x11, v8[--p5] = m9;
    } else g6 == -3 ? u5 = m9 : g6 == -4 && (o4 = m9);
    return p5;
  }
  let P12 = [], j12 = [];
  for (; h3.pos > 0; ) d5(l11.start || 0, l11.bufferStart || 0, P12, j12, -1);
  let _11 = (e4 = l11.length) !== null && e4 !== void 0 ? e4 : P12.length ? j12[0] + P12[0].length : 0;
  return new z3(f2[l11.topID], P12.reverse(), j12.reverse(), _11);
}
var me3 = /* @__PURE__ */ new WeakMap();
function Q3(l11, e4) {
  if (!l11.isAnonymous || e4 instanceof W3 || e4.type != l11) return 1;
  let t5 = me3.get(e4);
  if (t5 == null) {
    t5 = 1;
    for (let r2 of e4.children) {
      if (r2.type != l11 || !(r2 instanceof z3)) {
        t5 = 1;
        break;
      }
      t5 += Q3(l11, r2);
    }
    me3.set(e4, t5);
  }
  return t5;
}
function ae3(l11, e4, t5, r2, i9, n22, s99, h3, f2) {
  let u5 = 0;
  for (let c4 = r2; c4 < i9; c4++) u5 += Q3(l11, e4[c4]);
  let o4 = Math.ceil(u5 * 1.5 / 8), d5 = [], a2 = [];
  function y10(c4, S11, O9, P12, j12) {
    for (let _11 = O9; _11 < P12; ) {
      let x11 = _11, v8 = S11[_11], p5 = Q3(l11, c4[_11]);
      for (_11++; _11 < P12; _11++) {
        let m9 = Q3(l11, c4[_11]);
        if (p5 + m9 >= o4) break;
        p5 += m9;
      }
      if (_11 == x11 + 1) {
        if (p5 > o4) {
          let m9 = c4[x11];
          y10(m9.children, m9.positions, 0, m9.children.length, S11[x11] + j12);
          continue;
        }
        d5.push(c4[x11]);
      } else {
        let m9 = S11[_11 - 1] + c4[_11 - 1].length - v8;
        d5.push(ae3(l11, c4, S11, x11, _11, v8, m9, null, f2));
      }
      a2.push(v8 + j12 - n22);
    }
  }
  return y10(e4, t5, r2, i9, 0), (h3 || f2)(d5, a2, s99);
}
var Z3 = class l8 {
  constructor(e4, t5, r2, i9, n22 = false, s99 = false) {
    this.from = e4, this.to = t5, this.tree = r2, this.offset = i9, this.open = (n22 ? 1 : 0) | (s99 ? 2 : 0);
  }
  get openStart() {
    return (this.open & 1) > 0;
  }
  get openEnd() {
    return (this.open & 2) > 0;
  }
  static addTree(e4, t5 = [], r2 = false) {
    let i9 = [
      new l8(0, e4.length, e4, 0, false, r2)
    ];
    for (let n22 of t5) n22.to > e4.length && i9.push(n22);
    return i9;
  }
  static applyChanges(e4, t5, r2 = 128) {
    if (!t5.length) return e4;
    let i9 = [], n22 = 1, s99 = e4.length ? e4[0] : null;
    for (let h3 = 0, f2 = 0, u5 = 0; ; h3++) {
      let o4 = h3 < t5.length ? t5[h3] : null, d5 = o4 ? o4.fromA : 1e9;
      if (d5 - f2 >= r2) for (; s99 && s99.from < d5; ) {
        let a2 = s99;
        if (f2 >= a2.from || d5 <= a2.to || u5) {
          let y10 = Math.max(a2.from, f2) - u5, c4 = Math.min(a2.to, d5) - u5;
          a2 = y10 >= c4 ? null : new l8(y10, c4, a2.tree, a2.offset + u5, h3 > 0, !!o4);
        }
        if (a2 && i9.push(a2), s99.to > d5) break;
        s99 = n22 < e4.length ? e4[n22++] : null;
      }
      if (!o4) break;
      f2 = o4.toA, u5 = o4.toA - o4.toB;
    }
    return i9;
  }
};
var ye3 = class {
  startParse(e4, t5, r2) {
    return typeof e4 == "string" && (e4 = new se3(e4)), r2 = r2 ? r2.length ? r2.map((i9) => new N3(i9.from, i9.to)) : [
      new N3(0, 0)
    ] : [
      new N3(0, e4.length)
    ], this.createParse(e4, t5 || [], r2);
  }
  parse(e4, t5, r2) {
    let i9 = this.startParse(e4, t5, r2);
    for (; ; ) {
      let n22 = i9.advance();
      if (n22) return n22;
    }
  }
};
var se3 = class {
  constructor(e4) {
    this.string = e4;
  }
  get length() {
    return this.string.length;
  }
  chunk(e4) {
    return this.string.slice(e4);
  }
  get lineChunks() {
    return false;
  }
  read(e4, t5) {
    return this.string.slice(e4, t5);
  }
};
var he3 = new w3({
  perNode: true
});

// deno:https://esm.sh/@lezer/highlight@0.16.0/denonext/highlight.mjs
var L2 = 0;
var y3 = class o {
  constructor(e4, a2, i9) {
    this.set = e4, this.base = a2, this.modified = i9, this.id = L2++;
  }
  static define(e4) {
    if (e4?.base) throw new Error("Can not derive from a modified tag");
    let a2 = new o([], null, []);
    if (a2.set.push(a2), e4) for (let i9 of e4.set) a2.set.push(i9);
    return a2;
  }
  static defineModifier() {
    let e4 = new C3();
    return (a2) => a2.modified.indexOf(e4) > -1 ? a2 : C3.get(a2.base || a2, a2.modified.concat(e4).sort((i9, n22) => i9.id - n22.id));
  }
};
var Q4 = 0;
var C3 = class o2 {
  constructor() {
    this.instances = [], this.id = Q4++;
  }
  static get(e4, a2) {
    if (!a2.length) return e4;
    let i9 = a2[0].instances.find((r2) => r2.base == e4 && U3(a2, r2.modified));
    if (i9) return i9;
    let n22 = [], l11 = new y3(n22, e4, a2);
    for (let r2 of a2) r2.instances.push(l11);
    let c4 = V4(a2);
    for (let r2 of e4.set) for (let p5 of c4) n22.push(o2.get(r2, p5));
    return l11;
  }
};
function U3(o4, e4) {
  return o4.length == e4.length && o4.every((a2, i9) => a2 == e4[i9]);
}
function V4(o4) {
  let e4 = [
    o4
  ];
  for (let a2 = 0; a2 < o4.length; a2++) for (let i9 of V4(o4.slice(0, a2).concat(o4.slice(a2 + 1)))) e4.push(i9);
  return e4;
}
function Z4(o4) {
  let e4 = /* @__PURE__ */ Object.create(null);
  for (let a2 in o4) {
    let i9 = o4[a2];
    Array.isArray(i9) || (i9 = [
      i9
    ]);
    for (let n22 of a2.split(" ")) if (n22) {
      let l11 = [], c4 = 2, r2 = n22;
      for (let m9 = 0; ; ) {
        if (r2 == "..." && m9 > 0 && m9 + 3 == n22.length) {
          c4 = 1;
          break;
        }
        let f2 = /^"(?:[^"\\]|\\.)*?"|[^\/!]+/.exec(r2);
        if (!f2) throw new RangeError("Invalid path: " + n22);
        if (l11.push(f2[0] == "*" ? "" : f2[0][0] == '"' ? JSON.parse(f2[0]) : f2[0]), m9 += f2[0].length, m9 == n22.length) break;
        let h3 = n22[m9++];
        if (m9 == n22.length && h3 == "!") {
          c4 = 0;
          break;
        }
        if (h3 != "/") throw new RangeError("Invalid path: " + n22);
        r2 = n22.slice(m9);
      }
      let p5 = l11.length - 1, g6 = l11[p5];
      if (!g6) throw new RangeError("Invalid path: " + n22);
      let d5 = new q3(i9, c4, p5 > 0 ? l11.slice(0, p5) : null);
      e4[g6] = d5.sort(e4[g6]);
    }
  }
  return z4.add(e4);
}
var z4 = new w3();
var q3 = class {
  constructor(e4, a2, i9, n22) {
    this.tags = e4, this.mode = a2, this.context = i9, this.next = n22;
  }
  sort(e4) {
    return !e4 || e4.depth < this.depth ? (this.next = e4, this) : (e4.next = this.sort(e4.next), e4);
  }
  get depth() {
    return this.context ? this.context.length : 0;
  }
};
function W4(o4, e4) {
  let a2 = /* @__PURE__ */ Object.create(null);
  for (let l11 of o4) if (!Array.isArray(l11.tag)) a2[l11.tag.id] = l11.class;
  else for (let c4 of l11.tag) a2[c4.id] = l11.class;
  let { scope: i9, all: n22 = null } = e4 || {};
  return {
    style: (l11) => {
      let c4 = n22;
      for (let r2 of l11) for (let p5 of r2.set) {
        let g6 = a2[p5.id];
        if (g6) {
          c4 = c4 ? c4 + " " + g6 : g6;
          break;
        }
      }
      return c4;
    },
    scope: i9
  };
}
function X4(o4, e4) {
  let a2 = null;
  for (let i9 of o4) {
    let n22 = i9.style(e4);
    n22 && (a2 = a2 ? a2 + " " + n22 : n22);
  }
  return a2;
}
function $3(o4, e4, a2, i9 = 0, n22 = o4.length) {
  let l11 = new P3(i9, Array.isArray(e4) ? e4 : [
    e4
  ], a2);
  l11.highlightRange(o4.cursor(), i9, n22, "", l11.highlighters), l11.flush(n22);
}
var P3 = class {
  constructor(e4, a2, i9) {
    this.at = e4, this.highlighters = a2, this.span = i9, this.class = "";
  }
  startSpan(e4, a2) {
    a2 != this.class && (this.flush(e4), e4 > this.at && (this.at = e4), this.class = a2);
  }
  flush(e4) {
    e4 > this.at && this.class && this.span(this.at, e4, this.class);
  }
  highlightRange(e4, a2, i9, n22, l11) {
    let { type: c4, from: r2, to: p5 } = e4;
    if (r2 >= i9 || p5 <= a2) return;
    c4.isTop && (l11 = this.highlighters.filter((h3) => !h3.scope || h3.scope(c4)));
    let g6 = n22, d5 = c4.prop(z4), m9 = false;
    for (; d5; ) {
      if (!d5.context || e4.matchContext(d5.context)) {
        let h3 = X4(l11, d5.tags);
        h3 && (g6 && (g6 += " "), g6 += h3, d5.mode == 1 ? n22 += (n22 ? " " : "") + h3 : d5.mode == 0 && (m9 = true));
        break;
      }
      d5 = d5.next;
    }
    if (this.startSpan(e4.from, g6), m9) return;
    let f2 = e4.tree && e4.tree.prop(w3.mounted);
    if (f2 && f2.overlay) {
      let h3 = e4.node.enter(f2.overlay[0].from + r2, 1), G12 = this.highlighters.filter((v8) => !v8.scope || v8.scope(f2.tree.type)), D9 = e4.firstChild();
      for (let v8 = 0, M14 = r2; ; v8++) {
        let O9 = v8 < f2.overlay.length ? f2.overlay[v8] : null, T12 = O9 ? O9.from + r2 : p5, H10 = Math.max(a2, M14), E12 = Math.min(i9, T12);
        if (H10 < E12 && D9) for (; e4.from < E12 && (this.highlightRange(e4, H10, E12, n22, l11), this.startSpan(Math.min(i9, e4.to), g6), !(e4.to >= T12 || !e4.nextSibling())); ) ;
        if (!O9 || T12 > i9) break;
        M14 = O9.to + r2, M14 > a2 && (this.highlightRange(h3.cursor(), Math.max(a2, O9.from + r2), Math.min(i9, M14), n22, G12), this.startSpan(M14, g6));
      }
      D9 && e4.parent();
    } else if (e4.firstChild()) {
      do
        if (!(e4.to <= a2)) {
          if (e4.from >= i9) break;
          this.highlightRange(e4, a2, i9, n22, l11), this.startSpan(Math.min(i9, e4.to), g6);
        }
      while (e4.nextSibling());
      e4.parent();
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
var c2 = class {
  constructor(t5, e4, r2 = []) {
    this.data = t5, I.prototype.hasOwnProperty("tree") || Object.defineProperty(I.prototype, "tree", {
      get() {
        return m3(this);
      }
    }), this.parser = e4, this.extension = [
      x3.of(this),
      I.languageData.of((i9, s99, o4) => i9.facet(at3(i9, s99, o4)))
    ].concat(r2);
  }
  isActiveAt(t5, e4, r2 = -1) {
    return at3(t5, e4, r2) == this.data;
  }
  findRegions(t5) {
    let e4 = t5.facet(x3);
    if (e4?.data == this.data) return [
      {
        from: 0,
        to: t5.doc.length
      }
    ];
    if (!e4 || !e4.allowsNesting) return [];
    let r2 = [], i9 = (s99, o4) => {
      if (s99.prop(C4) == this.data) {
        r2.push({
          from: o4,
          to: o4 + s99.length
        });
        return;
      }
      let a2 = s99.prop(w3.mounted);
      if (a2) {
        if (a2.tree.prop(C4) == this.data) {
          if (a2.overlay) for (let l11 of a2.overlay) r2.push({
            from: l11.from + o4,
            to: l11.to + o4
          });
          else r2.push({
            from: o4,
            to: o4 + s99.length
          });
          return;
        } else if (a2.overlay) {
          let l11 = r2.length;
          if (i9(a2.tree, a2.overlay[0].from + o4), r2.length > l11) return;
        }
      }
      for (let l11 = 0; l11 < s99.children.length; l11++) {
        let h3 = s99.children[l11];
        h3 instanceof z3 && i9(h3, s99.positions[l11] + o4);
      }
    };
    return i9(m3(t5), 0), r2;
  }
  get allowsNesting() {
    return true;
  }
};
c2.setState = v.define();
function at3(n22, t5, e4) {
  let r2 = n22.facet(x3);
  if (!r2) return null;
  let i9 = r2.data;
  if (r2.allowsNesting) for (let s99 = m3(n22).topNode; s99; s99 = s99.enter(t5, e4, A2.ExcludeBuffers)) i9 = s99.type.prop(C4) || i9;
  return i9;
}
function m3(n22) {
  let t5 = n22.field(c2.state, false);
  return t5 ? t5.tree : z3.empty;
}
var Y3 = class {
  constructor(t5, e4 = t5.length) {
    this.doc = t5, this.length = e4, this.cursorPos = 0, this.string = "", this.cursor = t5.iter();
  }
  syncTo(t5) {
    return this.string = this.cursor.next(t5 - this.cursorPos).value, this.cursorPos = t5 + this.string.length, this.cursorPos - this.string.length;
  }
  chunk(t5) {
    return this.syncTo(t5), this.string;
  }
  get lineChunks() {
    return true;
  }
  read(t5, e4) {
    let r2 = this.cursorPos - this.string.length;
    return t5 < r2 || e4 >= this.cursorPos ? this.doc.sliceString(t5, e4) : this.string.slice(t5 - r2, e4 - r2);
  }
};
var A4 = null;
var I4 = class n2 {
  constructor(t5, e4, r2 = [], i9, s99, o4, a2, l11) {
    this.parser = t5, this.state = e4, this.fragments = r2, this.tree = i9, this.treeLen = s99, this.viewport = o4, this.skipped = a2, this.scheduleOn = l11, this.parse = null, this.tempSkipped = [];
  }
  static create(t5, e4, r2) {
    return new n2(t5, e4, [], z3.empty, 0, r2, [], null);
  }
  startParse() {
    return this.parser.startParse(new Y3(this.state.doc), this.fragments);
  }
  work(t5, e4) {
    return e4 != null && e4 >= this.state.doc.length && (e4 = void 0), this.tree != z3.empty && this.isDone(e4 ?? this.state.doc.length) ? (this.takeTree(), true) : this.withContext(() => {
      var r2;
      if (typeof t5 == "number") {
        let i9 = Date.now() + t5;
        t5 = () => Date.now() > i9;
      }
      for (this.parse || (this.parse = this.startParse()), e4 != null && (this.parse.stoppedAt == null || this.parse.stoppedAt > e4) && e4 < this.state.doc.length && this.parse.stopAt(e4); ; ) {
        let i9 = this.parse.advance();
        if (i9) if (this.fragments = this.withoutTempSkipped(Z3.addTree(i9, this.fragments, this.parse.stoppedAt != null)), this.treeLen = (r2 = this.parse.stoppedAt) !== null && r2 !== void 0 ? r2 : this.state.doc.length, this.tree = i9, this.parse = null, this.treeLen < (e4 ?? this.state.doc.length)) this.parse = this.startParse();
        else return true;
        if (t5()) return false;
      }
    });
  }
  takeTree() {
    let t5, e4;
    this.parse && (t5 = this.parse.parsedPos) >= this.treeLen && ((this.parse.stoppedAt == null || this.parse.stoppedAt > t5) && this.parse.stopAt(t5), this.withContext(() => {
      for (; !(e4 = this.parse.advance()); ) ;
    }), this.treeLen = t5, this.tree = e4, this.fragments = this.withoutTempSkipped(Z3.addTree(this.tree, this.fragments, true)), this.parse = null);
  }
  withContext(t5) {
    let e4 = A4;
    A4 = this;
    try {
      return t5();
    } finally {
      A4 = e4;
    }
  }
  withoutTempSkipped(t5) {
    for (let e4; e4 = this.tempSkipped.pop(); ) t5 = ft2(t5, e4.from, e4.to);
    return t5;
  }
  changes(t5, e4) {
    let { fragments: r2, tree: i9, treeLen: s99, viewport: o4, skipped: a2 } = this;
    if (this.takeTree(), !t5.empty) {
      let l11 = [];
      if (t5.iterChangedRanges((h3, u5, d5, g6) => l11.push({
        fromA: h3,
        toA: u5,
        fromB: d5,
        toB: g6
      })), r2 = Z3.applyChanges(r2, l11), i9 = z3.empty, s99 = 0, o4 = {
        from: t5.mapPos(o4.from, -1),
        to: t5.mapPos(o4.to, 1)
      }, this.skipped.length) {
        a2 = [];
        for (let h3 of this.skipped) {
          let u5 = t5.mapPos(h3.from, 1), d5 = t5.mapPos(h3.to, -1);
          u5 < d5 && a2.push({
            from: u5,
            to: d5
          });
        }
      }
    }
    return new n2(this.parser, e4, r2, i9, s99, o4, a2, this.scheduleOn);
  }
  updateViewport(t5) {
    if (this.viewport.from == t5.from && this.viewport.to == t5.to) return false;
    this.viewport = t5;
    let e4 = this.skipped.length;
    for (let r2 = 0; r2 < this.skipped.length; r2++) {
      let { from: i9, to: s99 } = this.skipped[r2];
      i9 < t5.to && s99 > t5.from && (this.fragments = ft2(this.fragments, i9, s99), this.skipped.splice(r2--, 1));
    }
    return this.skipped.length >= e4 ? false : (this.reset(), true);
  }
  reset() {
    this.parse && (this.takeTree(), this.parse = null);
  }
  skipUntilInView(t5, e4) {
    this.skipped.push({
      from: t5,
      to: e4
    });
  }
  static getSkippingParser(t5) {
    return new class extends ye3 {
      createParse(e4, r2, i9) {
        let s99 = i9[0].from, o4 = i9[i9.length - 1].to;
        return {
          parsedPos: s99,
          advance() {
            let l11 = A4;
            if (l11) {
              for (let h3 of i9) l11.tempSkipped.push(h3);
              t5 && (l11.scheduleOn = l11.scheduleOn ? Promise.all([
                l11.scheduleOn,
                t5
              ]) : t5);
            }
            return this.parsedPos = o4, new z3(T4.none, [], [], o4 - s99);
          },
          stoppedAt: null,
          stopAt() {
          }
        };
      }
    }();
  }
  isDone(t5) {
    t5 = Math.min(t5, this.state.doc.length);
    let e4 = this.fragments;
    return this.treeLen >= t5 && e4.length && e4[0].from == 0 && e4[0].to >= t5;
  }
  static get() {
    return A4;
  }
};
function ft2(n22, t5, e4) {
  return Z3.applyChanges(n22, [
    {
      fromA: t5,
      toA: e4,
      fromB: t5,
      toB: e4
    }
  ]);
}
var O3 = class n3 {
  constructor(t5) {
    this.context = t5, this.tree = t5.tree;
  }
  apply(t5) {
    if (!t5.docChanged && this.tree == this.context.tree) return this;
    let e4 = this.context.changes(t5.changes, t5.state), r2 = this.context.treeLen == t5.startState.doc.length ? void 0 : Math.max(t5.changes.mapPos(this.context.treeLen), e4.viewport.to);
    return e4.work(20, r2) || e4.takeTree(), new n3(e4);
  }
  static init(t5) {
    let e4 = Math.min(3e3, t5.doc.length), r2 = I4.create(t5.facet(x3).parser, t5, {
      from: 0,
      to: e4
    });
    return r2.work(20, e4) || r2.takeTree(), new n3(r2);
  }
};
c2.state = $.define({
  create: O3.init,
  update(n22, t5) {
    for (let e4 of t5.effects) if (e4.is(c2.setState)) return e4.value;
    return t5.startState.facet(x3) != t5.state.facet(x3) ? O3.init(t5.state) : n22.apply(t5);
  }
});
var vt2 = (n22) => {
  let t5 = setTimeout(() => n22(), 500);
  return () => clearTimeout(t5);
};
typeof requestIdleCallback < "u" && (vt2 = (n22) => {
  let t5 = -1, e4 = setTimeout(() => {
    t5 = requestIdleCallback(n22, {
      timeout: 400
    });
  }, 100);
  return () => t5 < 0 ? clearTimeout(e4) : cancelIdleCallback(t5);
});
var Q5 = typeof navigator < "u" && (!((K5 = navigator.scheduling) === null || K5 === void 0) && K5.isInputPending) ? () => navigator.scheduling.isInputPending() : null;
var xt2 = P2.fromClass(class {
  constructor(t5) {
    this.view = t5, this.working = null, this.workScheduled = 0, this.chunkEnd = -1, this.chunkBudget = -1, this.work = this.work.bind(this), this.scheduleWork();
  }
  update(t5) {
    let e4 = this.view.state.field(c2.state).context;
    (e4.updateViewport(t5.view.viewport) || this.view.viewport.to > e4.treeLen) && this.scheduleWork(), t5.docChanged && (this.view.hasFocus && (this.chunkBudget += 50), this.scheduleWork()), this.checkAsyncSchedule(e4);
  }
  scheduleWork() {
    if (this.working) return;
    let { state: t5 } = this.view, e4 = t5.field(c2.state);
    (e4.tree != e4.context.tree || !e4.context.isDone(t5.doc.length)) && (this.working = vt2(this.work));
  }
  work(t5) {
    this.working = null;
    let e4 = Date.now();
    if (this.chunkEnd < e4 && (this.chunkEnd < 0 || this.view.hasFocus) && (this.chunkEnd = e4 + 3e4, this.chunkBudget = 3e3), this.chunkBudget <= 0) return;
    let { state: r2, viewport: { to: i9 } } = this.view, s99 = r2.field(c2.state);
    if (s99.tree == s99.context.tree && s99.context.isDone(i9 + 1e5)) return;
    let o4 = Date.now() + Math.min(this.chunkBudget, 100, t5 && !Q5 ? Math.max(25, t5.timeRemaining() - 5) : 1e9), a2 = s99.context.treeLen < i9 && r2.doc.length > i9 + 1e3, l11 = s99.context.work(() => Q5 && Q5() || Date.now() > o4, i9 + (a2 ? 0 : 1e5));
    this.chunkBudget -= Date.now() - e4, (l11 || this.chunkBudget <= 0) && (s99.context.takeTree(), this.view.dispatch({
      effects: c2.setState.of(new O3(s99.context))
    })), this.chunkBudget > 0 && !(l11 && !a2) && this.scheduleWork(), this.checkAsyncSchedule(s99.context);
  }
  checkAsyncSchedule(t5) {
    t5.scheduleOn && (this.workScheduled++, t5.scheduleOn.then(() => this.scheduleWork()).catch((e4) => Z2(this.view.state, e4)).then(() => this.workScheduled--), t5.scheduleOn = null);
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
  combine(n22) {
    return n22.length ? n22[0] : null;
  },
  enables: [
    c2.state,
    xt2
  ]
});
var St = y.define();
var Pt2 = y.define({
  combine: (n22) => {
    if (!n22.length) return "  ";
    if (!/^(?: +|\t+)$/.test(n22[0])) throw new Error("Invalid indent unit: " + JSON.stringify(n22[0]));
    return n22[0];
  }
});
function L3(n22) {
  let t5 = n22.facet(Pt2);
  return t5.charCodeAt(0) == 9 ? n22.tabSize * t5.length : t5.length;
}
function te3(n22, t5) {
  let e4 = "", r2 = n22.tabSize;
  if (n22.facet(Pt2).charCodeAt(0) == 9) for (; t5 >= r2; ) e4 += "	", t5 -= r2;
  for (let i9 = 0; i9 < t5; i9++) e4 += " ";
  return e4;
}
function ee3(n22, t5) {
  n22 instanceof I && (n22 = new R4(n22));
  for (let r2 of n22.state.facet(St)) {
    let i9 = r2(n22, t5);
    if (i9 != null) return i9;
  }
  let e4 = m3(n22.state);
  return e4 ? re3(n22, e4, t5) : null;
}
var R4 = class {
  constructor(t5, e4 = {}) {
    this.state = t5, this.options = e4, this.unit = L3(t5);
  }
  lineAt(t5, e4 = 1) {
    let r2 = this.state.doc.lineAt(t5), { simulateBreak: i9, simulateDoubleBreak: s99 } = this.options;
    return i9 != null && i9 >= r2.from && i9 <= r2.to ? s99 && i9 == t5 ? {
      text: "",
      from: t5
    } : (e4 < 0 ? i9 < t5 : i9 <= t5) ? {
      text: r2.text.slice(i9 - r2.from),
      from: i9
    } : {
      text: r2.text.slice(0, i9 - r2.from),
      from: r2.from
    } : r2;
  }
  textAfterPos(t5, e4 = 1) {
    if (this.options.simulateDoubleBreak && t5 == this.options.simulateBreak) return "";
    let { text: r2, from: i9 } = this.lineAt(t5, e4);
    return r2.slice(t5 - i9, Math.min(r2.length, t5 + 100 - i9));
  }
  column(t5, e4 = 1) {
    let { text: r2, from: i9 } = this.lineAt(t5, e4), s99 = this.countColumn(r2, t5 - i9), o4 = this.options.overrideIndentation ? this.options.overrideIndentation(i9) : -1;
    return o4 > -1 && (s99 += o4 - this.countColumn(r2, r2.search(/\S|$/))), s99;
  }
  countColumn(t5, e4 = t5.length) {
    return ot(t5, this.state.tabSize, e4);
  }
  lineIndent(t5, e4 = 1) {
    let { text: r2, from: i9 } = this.lineAt(t5, e4), s99 = this.options.overrideIndentation;
    if (s99) {
      let o4 = s99(i9);
      if (o4 > -1) return o4;
    }
    return this.countColumn(r2, r2.search(/\S|$/));
  }
  get simulatedBreak() {
    return this.options.simulateBreak || null;
  }
};
var ne4 = new w3();
function re3(n22, t5, e4) {
  return Ct2(t5.resolveInner(e4).enterUnfinishedNodesBefore(e4), e4, n22);
}
function ie4(n22) {
  return n22.pos == n22.options.simulateBreak && n22.options.simulateDoubleBreak;
}
function se4(n22) {
  let t5 = n22.type.prop(ne4);
  if (t5) return t5;
  let e4 = n22.firstChild, r2;
  if (e4 && (r2 = e4.type.prop(w3.closedBy))) {
    let i9 = n22.lastChild, s99 = i9 && r2.indexOf(i9.name) > -1;
    return (o4) => At2(o4, true, 1, void 0, s99 && !ie4(o4) ? i9.from : void 0);
  }
  return n22.parent == null ? oe3 : null;
}
function Ct2(n22, t5, e4) {
  for (; n22; n22 = n22.parent) {
    let r2 = se4(n22);
    if (r2) return r2(Z5.create(e4, t5, n22));
  }
  return null;
}
function oe3() {
  return 0;
}
var Z5 = class n4 extends R4 {
  constructor(t5, e4, r2) {
    super(t5.state, t5.options), this.base = t5, this.pos = e4, this.node = r2;
  }
  static create(t5, e4, r2) {
    return new n4(t5, e4, r2);
  }
  get textAfter() {
    return this.textAfterPos(this.pos);
  }
  get baseIndent() {
    let t5 = this.state.doc.lineAt(this.node.from);
    for (; ; ) {
      let e4 = this.node.resolve(t5.from);
      for (; e4.parent && e4.parent.from == e4.from; ) e4 = e4.parent;
      if (le2(e4, this.node)) break;
      t5 = this.state.doc.lineAt(e4.from);
    }
    return this.lineIndent(t5.from);
  }
  continue() {
    let t5 = this.node.parent;
    return t5 ? Ct2(t5, this.pos, this.base) : 0;
  }
};
function le2(n22, t5) {
  for (let e4 = t5; e4; e4 = e4.parent) if (n22 == e4) return true;
  return false;
}
function ae4(n22) {
  let t5 = n22.node, e4 = t5.childAfter(t5.from), r2 = t5.lastChild;
  if (!e4) return null;
  let i9 = n22.options.simulateBreak, s99 = n22.state.doc.lineAt(e4.from), o4 = i9 == null || i9 <= s99.from ? s99.to : Math.min(s99.to, i9);
  for (let a2 = e4.to; ; ) {
    let l11 = t5.childAfter(a2);
    if (!l11 || l11 == r2) return null;
    if (!l11.type.isSkipped) return l11.from < o4 ? e4 : null;
    a2 = l11.to;
  }
}
function At2(n22, t5, e4, r2, i9) {
  let s99 = n22.textAfter, o4 = s99.match(/^\s*/)[0].length, a2 = r2 && s99.slice(o4, o4 + r2.length) == r2 || i9 == n22.pos + o4, l11 = t5 ? ae4(n22) : null;
  return l11 ? a2 ? n22.column(l11.from) : n22.column(l11.to) : n22.baseIndent + (a2 ? 0 : n22.unit * e4);
}
var he4 = 200;
function Xe3() {
  return I.transactionFilter.of((n22) => {
    if (!n22.docChanged || !n22.isUserEvent("input.type") && !n22.isUserEvent("input.complete")) return n22;
    let t5 = n22.startState.languageDataAt("indentOnInput", n22.startState.selection.main.head);
    if (!t5.length) return n22;
    let e4 = n22.newDoc, { head: r2 } = n22.newSelection.main, i9 = e4.lineAt(r2);
    if (r2 > i9.from + he4) return n22;
    let s99 = e4.sliceString(i9.from, r2);
    if (!t5.some((h3) => h3.test(s99))) return n22;
    let { state: o4 } = n22, a2 = -1, l11 = [];
    for (let { head: h3 } of o4.selection.ranges) {
      let u5 = o4.doc.lineAt(h3);
      if (u5.from == a2) continue;
      a2 = u5.from;
      let d5 = ee3(o4, u5.from);
      if (d5 == null) continue;
      let g6 = /^\s*/.exec(u5.text)[0], b9 = te3(o4, d5);
      g6 != b9 && l11.push({
        from: u5.from,
        to: u5.from + g6.length,
        insert: b9
      });
    }
    return l11.length ? [
      n22,
      {
        changes: l11,
        sequential: true
      }
    ] : n22;
  });
}
var fe3 = y.define();
var ue4 = new w3();
function ce4(n22, t5, e4) {
  let r2 = m3(n22);
  if (r2.length < e4) return null;
  let i9 = r2.resolveInner(e4), s99 = null;
  for (let o4 = i9; o4; o4 = o4.parent) {
    if (o4.to <= e4 || o4.from > e4) continue;
    if (s99 && o4.from < t5) break;
    let a2 = o4.type.prop(ue4);
    if (a2 && (o4.to < r2.length - 50 || r2.length == n22.doc.length || !de3(o4))) {
      let l11 = a2(o4, n22);
      l11 && l11.from <= e4 && l11.from >= t5 && l11.to > e4 && (s99 = l11);
    }
  }
  return s99;
}
function de3(n22) {
  let t5 = n22.lastChild;
  return t5 && t5.to == n22.to && t5.type.isError;
}
function U4(n22, t5, e4) {
  for (let r2 of n22.facet(fe3)) {
    let i9 = r2(n22, t5, e4);
    if (i9) return i9;
  }
  return ce4(n22, t5, e4);
}
function Tt2(n22, t5) {
  let e4 = t5.mapPos(n22.from, 1), r2 = t5.mapPos(n22.to, -1);
  return e4 >= r2 ? void 0 : {
    from: e4,
    to: r2
  };
}
var H3 = v.define({
  map: Tt2
});
var N5 = v.define({
  map: Tt2
});
function Dt2(n22) {
  let t5 = [];
  for (let { head: e4 } of n22.state.selection.ranges) t5.some((r2) => r2.from <= e4 && r2.to >= e4) || t5.push(n22.lineBlockAt(e4));
  return t5;
}
var S4 = $.define({
  create() {
    return C2.none;
  },
  update(n22, t5) {
    n22 = n22.map(t5.changes);
    for (let e4 of t5.effects) e4.is(H3) && !pe3(n22, e4.value.from, e4.value.to) ? n22 = n22.update({
      add: [
        ye4.range(e4.value.from, e4.value.to)
      ]
    }) : e4.is(N5) && (n22 = n22.update({
      filter: (r2, i9) => e4.value.from != r2 || e4.value.to != i9,
      filterFrom: e4.value.from,
      filterTo: e4.value.to
    }));
    if (t5.selection) {
      let e4 = false, { head: r2 } = t5.selection.main;
      n22.between(r2, r2, (i9, s99) => {
        i9 < r2 && s99 > r2 && (e4 = true);
      }), e4 && (n22 = n22.update({
        filterFrom: r2,
        filterTo: r2,
        filter: (i9, s99) => s99 <= r2 || i9 >= r2
      }));
    }
    return n22;
  },
  provide: (n22) => M2.decorations.from(n22)
});
function W5(n22, t5, e4) {
  var r2;
  let i9 = null;
  return (r2 = n22.field(S4, false)) === null || r2 === void 0 || r2.between(t5, e4, (s99, o4) => {
    (!i9 || i9.from > s99) && (i9 = {
      from: s99,
      to: o4
    });
  }), i9;
}
function pe3(n22, t5, e4) {
  let r2 = false;
  return n22.between(t5, t5, (i9, s99) => {
    i9 == t5 && s99 == e4 && (r2 = true);
  }), r2;
}
function It2(n22, t5) {
  return n22.field(S4, false) ? t5 : t5.concat(v.appendConfig.of(Nt2()));
}
var me4 = (n22) => {
  for (let t5 of Dt2(n22)) {
    let e4 = U4(n22.state, t5.from, t5.to);
    if (e4) return n22.dispatch({
      effects: It2(n22.state, [
        H3.of(e4),
        Ot2(n22, e4)
      ])
    }), true;
  }
  return false;
};
var ge4 = (n22) => {
  if (!n22.state.field(S4, false)) return false;
  let t5 = [];
  for (let e4 of Dt2(n22)) {
    let r2 = W5(n22.state, e4.from, e4.to);
    r2 && t5.push(N5.of(r2), Ot2(n22, r2, false));
  }
  return t5.length && n22.dispatch({
    effects: t5
  }), t5.length > 0;
};
function Ot2(n22, t5, e4 = true) {
  let r2 = n22.state.doc.lineAt(t5.from).number, i9 = n22.state.doc.lineAt(t5.to).number;
  return M2.announce.of(`${n22.state.phrase(e4 ? "Folded lines" : "Unfolded lines")} ${r2} ${n22.state.phrase("to")} ${i9}.`);
}
var ke4 = (n22) => {
  let { state: t5 } = n22, e4 = [];
  for (let r2 = 0; r2 < t5.doc.length; ) {
    let i9 = n22.lineBlockAt(r2), s99 = U4(t5, i9.from, i9.to);
    s99 && e4.push(H3.of(s99)), r2 = (s99 ? n22.lineBlockAt(s99.to) : i9).to + 1;
  }
  return e4.length && n22.dispatch({
    effects: It2(n22.state, e4)
  }), !!e4.length;
};
var be3 = (n22) => {
  let t5 = n22.state.field(S4, false);
  if (!t5 || !t5.size) return false;
  let e4 = [];
  return t5.between(0, n22.state.doc.length, (r2, i9) => {
    e4.push(N5.of({
      from: r2,
      to: i9
    }));
  }), n22.dispatch({
    effects: e4
  }), true;
};
var _e4 = [
  {
    key: "Ctrl-Shift-[",
    mac: "Cmd-Alt-[",
    run: me4
  },
  {
    key: "Ctrl-Shift-]",
    mac: "Cmd-Alt-]",
    run: ge4
  },
  {
    key: "Ctrl-Alt-[",
    run: ke4
  },
  {
    key: "Ctrl-Alt-]",
    run: be3
  }
];
var we3 = {
  placeholderDOM: null,
  placeholderText: "\u2026"
};
var Bt2 = y.define({
  combine(n22) {
    return ht(n22, we3);
  }
});
function Nt2(n22) {
  let t5 = [
    S4,
    xe3
  ];
  return n22 && t5.push(Bt2.of(n22)), t5;
}
var ye4 = C2.replace({
  widget: new class extends K2 {
    toDOM(n22) {
      let { state: t5 } = n22, e4 = t5.facet(Bt2), r2 = (s99) => {
        let o4 = n22.lineBlockAt(n22.posAtDOM(s99.target)), a2 = W5(n22.state, o4.from, o4.to);
        a2 && n22.dispatch({
          effects: N5.of(a2)
        }), s99.preventDefault();
      };
      if (e4.placeholderDOM) return e4.placeholderDOM(n22, r2);
      let i9 = document.createElement("span");
      return i9.textContent = e4.placeholderText, i9.setAttribute("aria-label", t5.phrase("folded code")), i9.title = t5.phrase("unfold"), i9.className = "cm-foldPlaceholder", i9.onclick = r2, i9;
    }
  }()
});
var ve3 = {
  openText: "\u2304",
  closedText: "\u203A",
  markerDOM: null,
  domEventHandlers: {}
};
var D3 = class extends I2 {
  constructor(t5, e4) {
    super(), this.config = t5, this.open = e4;
  }
  eq(t5) {
    return this.config == t5.config && this.open == t5.open;
  }
  toDOM(t5) {
    if (this.config.markerDOM) return this.config.markerDOM(this.open);
    let e4 = document.createElement("span");
    return e4.textContent = this.open ? this.config.openText : this.config.closedText, e4.title = t5.state.phrase(this.open ? "Fold line" : "Unfold line"), e4;
  }
};
function tn2(n22 = {}) {
  let t5 = Object.assign(Object.assign({}, ve3), n22), e4 = new D3(t5, true), r2 = new D3(t5, false), i9 = P2.fromClass(class {
    constructor(o4) {
      this.from = o4.viewport.from, this.markers = this.buildMarkers(o4);
    }
    update(o4) {
      (o4.docChanged || o4.viewportChanged || o4.startState.facet(x3) != o4.state.facet(x3) || o4.startState.field(S4, false) != o4.state.field(S4, false) || m3(o4.startState) != m3(o4.state)) && (this.markers = this.buildMarkers(o4.view));
    }
    buildMarkers(o4) {
      let a2 = new se();
      for (let l11 of o4.viewportLineBlocks) {
        let h3 = W5(o4.state, l11.from, l11.to) ? r2 : U4(o4.state, l11.from, l11.to) ? e4 : null;
        h3 && a2.add(l11.from, l11.from, h3);
      }
      return a2.finish();
    }
  }), { domEventHandlers: s99 } = t5;
  return [
    i9,
    mo({
      class: "cm-foldGutter",
      markers(o4) {
        var a2;
        return ((a2 = o4.plugin(i9)) === null || a2 === void 0 ? void 0 : a2.markers) || O.empty;
      },
      initialSpacer() {
        return new D3(t5, false);
      },
      domEventHandlers: Object.assign(Object.assign({}, s99), {
        click: (o4, a2, l11) => {
          if (s99.click && s99.click(o4, a2, l11)) return true;
          let h3 = W5(o4.state, a2.from, a2.to);
          if (h3) return o4.dispatch({
            effects: N5.of(h3)
          }), true;
          let u5 = U4(o4.state, a2.from, a2.to);
          return u5 ? (o4.dispatch({
            effects: H3.of(u5)
          }), true) : false;
        }
      })
    }),
    Nt2()
  ];
}
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
var j3 = class n5 {
  constructor(t5, e4) {
    let r2;
    function i9(a2) {
      let l11 = T2.newName();
      return (r2 || (r2 = /* @__PURE__ */ Object.create(null)))["." + l11] = a2, l11;
    }
    let s99 = typeof e4.all == "string" ? e4.all : e4.all ? i9(e4.all) : void 0, o4 = e4.scope;
    this.scope = o4 instanceof c2 ? (a2) => a2.prop(C4) == o4.data : o4 ? (a2) => a2 == o4 : void 0, this.style = W4(t5.map((a2) => ({
      tag: a2.tag,
      class: a2.class || i9(Object.assign({}, a2, {
        tag: null
      }))
    })), {
      all: s99
    }).style, this.module = r2 ? new T2(r2) : null, this.themeType = e4.themeType;
  }
  static define(t5, e4) {
    return new n5(t5, e4 || {});
  }
};
var _3 = y.define();
var Mt2 = y.define({
  combine(n22) {
    return n22.length ? [
      n22[0]
    ] : null;
  }
});
function F4(n22) {
  let t5 = n22.facet(_3);
  return t5.length ? t5 : n22.facet(Mt2);
}
function en2(n22, t5) {
  let e4 = [
    Se4
  ], r2;
  return n22 instanceof j3 && (n22.module && e4.push(M2.styleModule.of(n22.module)), r2 = n22.themeType), t5?.fallback ? e4.push(Mt2.of(n22)) : r2 ? e4.push(_3.computeN([
    M2.darkTheme
  ], (i9) => i9.facet(M2.darkTheme) == (r2 == "dark") ? [
    n22
  ] : [])) : e4.push(_3.of(n22)), e4;
}
var tt3 = class {
  constructor(t5) {
    this.markCache = /* @__PURE__ */ Object.create(null), this.tree = m3(t5.state), this.decorations = this.buildDeco(t5, F4(t5.state));
  }
  update(t5) {
    let e4 = m3(t5.state), r2 = F4(t5.state), i9 = r2 != F4(t5.startState);
    e4.length < t5.view.viewport.to && !i9 && e4.type == this.tree.type ? this.decorations = this.decorations.map(t5.changes) : (e4 != this.tree || t5.viewportChanged || i9) && (this.tree = e4, this.decorations = this.buildDeco(t5.view, r2));
  }
  buildDeco(t5, e4) {
    if (!e4 || !this.tree.length) return C2.none;
    let r2 = new se();
    for (let { from: i9, to: s99 } of t5.visibleRanges) $3(this.tree, e4, (o4, a2, l11) => {
      r2.add(o4, a2, this.markCache[l11] || (this.markCache[l11] = C2.mark({
        class: l11
      })));
    }, i9, s99);
    return r2.finish();
  }
};
var Se4 = lt.high(P2.fromClass(tt3, {
  decorations: (n22) => n22.decorations
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
  combine(n22) {
    return ht(n22, {
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
function Te3(n22) {
  let t5 = [], e4 = n22.matched ? Ce4 : Ae3;
  return t5.push(e4.range(n22.start.from, n22.start.to)), n22.end && t5.push(e4.range(n22.end.from, n22.end.to)), t5;
}
var De3 = $.define({
  create() {
    return C2.none;
  },
  update(n22, t5) {
    if (!t5.docChanged && !t5.selection) return n22;
    let e4 = [], r2 = t5.state.facet(Lt2);
    for (let i9 of t5.state.selection.ranges) {
      if (!i9.empty) continue;
      let s99 = M4(t5.state, i9.head, -1, r2) || i9.head > 0 && M4(t5.state, i9.head - 1, 1, r2) || r2.afterCursor && (M4(t5.state, i9.head, 1, r2) || i9.head < t5.state.doc.length && M4(t5.state, i9.head + 1, -1, r2));
      s99 && (e4 = e4.concat(r2.renderMatch(s99, t5.state)));
    }
    return C2.set(e4, true);
  },
  provide: (n22) => M2.decorations.from(n22)
});
var Ie3 = [
  De3,
  Pe3
];
function sn2(n22 = {}) {
  return [
    Lt2.of(n22),
    Ie3
  ];
}
function et2(n22, t5, e4) {
  let r2 = n22.prop(t5 < 0 ? w3.openedBy : w3.closedBy);
  if (r2) return r2;
  if (n22.name.length == 1) {
    let i9 = e4.indexOf(n22.name);
    if (i9 > -1 && i9 % 2 == (t5 < 0 ? 1 : 0)) return [
      e4[i9 + t5]
    ];
  }
  return null;
}
function M4(n22, t5, e4, r2 = {}) {
  let i9 = r2.maxScanDistance || Et2, s99 = r2.brackets || Ft, o4 = m3(n22), a2 = o4.resolveInner(t5, e4);
  for (let l11 = a2; l11; l11 = l11.parent) {
    let h3 = et2(l11.type, e4, s99);
    if (h3 && l11.from < l11.to) return Oe3(n22, t5, e4, l11, h3, s99);
  }
  return Be3(n22, t5, e4, o4, a2.type, i9, s99);
}
function Oe3(n22, t5, e4, r2, i9, s99) {
  let o4 = r2.parent, a2 = {
    from: r2.from,
    to: r2.to
  }, l11 = 0, h3 = o4?.cursor();
  if (h3 && (e4 < 0 ? h3.childBefore(r2.from) : h3.childAfter(r2.to))) do
    if (e4 < 0 ? h3.to <= r2.from : h3.from >= r2.to) {
      if (l11 == 0 && i9.indexOf(h3.type.name) > -1 && h3.from < h3.to) return {
        start: a2,
        end: {
          from: h3.from,
          to: h3.to
        },
        matched: true
      };
      if (et2(h3.type, e4, s99)) l11++;
      else if (et2(h3.type, -e4, s99) && (l11--, l11 == 0)) return {
        start: a2,
        end: h3.from == h3.to ? void 0 : {
          from: h3.from,
          to: h3.to
        },
        matched: false
      };
    }
  while (e4 < 0 ? h3.prevSibling() : h3.nextSibling());
  return {
    start: a2,
    matched: false
  };
}
function Be3(n22, t5, e4, r2, i9, s99, o4) {
  let a2 = e4 < 0 ? n22.sliceDoc(t5 - 1, t5) : n22.sliceDoc(t5, t5 + 1), l11 = o4.indexOf(a2);
  if (l11 < 0 || l11 % 2 == 0 != e4 > 0) return null;
  let h3 = {
    from: e4 < 0 ? t5 - 1 : t5,
    to: e4 > 0 ? t5 + 1 : t5
  }, u5 = n22.doc.iterRange(t5, e4 > 0 ? n22.doc.length : 0), d5 = 0;
  for (let g6 = 0; !u5.next().done && g6 <= s99; ) {
    let b9 = u5.value;
    e4 < 0 && (g6 += b9.length);
    let q13 = t5 + g6 * e4;
    for (let P12 = e4 > 0 ? 0 : b9.length - 1, $t7 = e4 > 0 ? b9.length : -1; P12 != $t7; P12 += e4) {
      let J8 = o4.indexOf(b9[P12]);
      if (!(J8 < 0 || r2.resolve(q13 + P12, 1).type != i9)) if (J8 % 2 == 0 == e4 > 0) d5++;
      else {
        if (d5 == 1) return {
          start: h3,
          end: {
            from: q13 + P12,
            to: q13 + P12 + 1
          },
          matched: J8 >> 1 == l11 >> 1
        };
        d5--;
      }
    }
    e4 > 0 && (g6 += b9.length);
  }
  return u5.done ? {
    start: h3,
    matched: false
  } : null;
}
var ot3 = /* @__PURE__ */ Object.create(null);
var B4 = [
  T4.none
];
var Fe3 = new ce3(B4);
var mt = [];
var Wt = /* @__PURE__ */ Object.create(null);
for (let [n22, t5] of [
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
]) Wt[n22] = jt2(ot3, t5);
var V5 = class {
  constructor(t5) {
    this.extra = t5, this.table = Object.assign(/* @__PURE__ */ Object.create(null), Wt);
  }
  resolve(t5) {
    return t5 ? this.table[t5] || (this.table[t5] = jt2(this.extra, t5)) : 0;
  }
};
var Le3 = new V5(ot3);
function X5(n22, t5) {
  mt.indexOf(n22) > -1 || (mt.push(n22), console.warn(t5));
}
function jt2(n22, t5) {
  let e4 = null;
  for (let s99 of t5.split(".")) {
    let o4 = n22[s99] || s44[s99];
    o4 ? typeof o4 == "function" ? e4 ? e4 = o4(e4) : X5(s99, `Modifier ${s99} used at start of tag`) : e4 ? X5(s99, `Tag ${s99} used as modifier`) : e4 = o4 : X5(s99, `Unknown highlighting tag ${s99}`);
  }
  if (!e4) return 0;
  let r2 = t5.replace(/ /g, "_"), i9 = T4.define({
    id: B4.length,
    name: r2,
    props: [
      Z4({
        [r2]: e4
      })
    ]
  });
  return B4.push(i9), i9.id;
}

// deno:https://esm.sh/@codemirror/autocomplete@0.20.3/denonext/autocomplete.mjs
var M5 = class {
  constructor(e4, t5, i9) {
    this.state = e4, this.pos = t5, this.explicit = i9, this.abortListeners = [];
  }
  tokenBefore(e4) {
    let t5 = m3(this.state).resolveInner(this.pos, -1);
    for (; t5 && e4.indexOf(t5.name) < 0; ) t5 = t5.parent;
    return t5 ? {
      from: t5.from,
      to: this.pos,
      text: this.state.sliceDoc(t5.from, this.pos),
      type: t5.type
    } : null;
  }
  matchBefore(e4) {
    let t5 = this.state.doc.lineAt(this.pos), i9 = Math.max(t5.from, this.pos - 250), o4 = t5.text.slice(i9 - t5.from, this.pos - t5.from), s99 = o4.search(Pe4(e4, false));
    return s99 < 0 ? null : {
      from: i9 + s99,
      to: this.pos,
      text: o4.slice(s99)
    };
  }
  get aborted() {
    return this.abortListeners == null;
  }
  addEventListener(e4, t5) {
    e4 == "abort" && this.abortListeners && this.abortListeners.push(t5);
  }
};
function ue5(n22) {
  let e4 = Object.keys(n22).join(""), t5 = /\w/.test(e4);
  return t5 && (e4 = e4.replace(/\w/g, "")), `[${t5 ? "\\w" : ""}${e4.replace(/[^\w\s]/g, "\\$&")}]`;
}
function Ye3(n22) {
  let e4 = /* @__PURE__ */ Object.create(null), t5 = /* @__PURE__ */ Object.create(null);
  for (let { label: o4 } of n22) {
    e4[o4[0]] = true;
    for (let s99 = 1; s99 < o4.length; s99++) t5[o4[s99]] = true;
  }
  let i9 = ue5(e4) + ue5(t5) + "*$";
  return [
    new RegExp("^" + i9),
    new RegExp(i9)
  ];
}
function Ge3(n22) {
  let e4 = n22.map((o4) => typeof o4 == "string" ? {
    label: o4
  } : o4), [t5, i9] = e4.every((o4) => /^\w+$/.test(o4.label)) ? [
    /\w*$/,
    /\w+$/
  ] : Ye3(e4);
  return (o4) => {
    let s99 = o4.matchBefore(i9);
    return s99 || o4.explicit ? {
      from: s99 ? s99.from : o4.pos,
      options: e4,
      validFor: t5
    } : null;
  };
}
var B5 = class {
  constructor(e4, t5, i9) {
    this.completion = e4, this.source = t5, this.match = i9;
  }
};
function x4(n22) {
  return n22.selection.main.head;
}
function Pe4(n22, e4) {
  var t5;
  let { source: i9 } = n22, o4 = e4 && i9[0] != "^", s99 = i9[i9.length - 1] != "$";
  return !o4 && !s99 ? n22 : new RegExp(`${o4 ? "^" : ""}(?:${i9})${s99 ? "$" : ""}`, (t5 = n22.flags) !== null && t5 !== void 0 ? t5 : n22.ignoreCase ? "i" : "");
}
var Ht2 = F.define();
function Je3(n22, e4, t5, i9) {
  return Object.assign(Object.assign({}, n22.changeByRange((o4) => {
    if (o4 == n22.selection.main) return {
      changes: {
        from: t5,
        to: i9,
        insert: e4
      },
      range: x.cursor(t5 + e4.length)
    };
    let s99 = i9 - t5;
    return !o4.empty || s99 && n22.sliceDoc(o4.from - s99, o4.from) != n22.sliceDoc(t5, i9) ? {
      range: o4
    } : {
      changes: {
        from: o4.from - s99,
        to: o4.from,
        insert: e4
      },
      range: x.cursor(o4.from - s99 + e4.length)
    };
  })), {
    userEvent: "input.complete"
  });
}
function Te4(n22, e4) {
  let t5 = e4.completion.apply || e4.completion.label, i9 = e4.source;
  typeof t5 == "string" ? n22.dispatch(Je3(n22.state, t5, i9.from, i9.to)) : t5(n22, e4.completion, i9.from, i9.to);
}
var he5 = /* @__PURE__ */ new WeakMap();
function Ze3(n22) {
  if (!Array.isArray(n22)) return n22;
  let e4 = he5.get(n22);
  return e4 || he5.set(n22, e4 = Ge3(n22)), e4;
}
var Q6 = class {
  constructor(e4) {
    this.pattern = e4, this.chars = [], this.folded = [], this.any = [], this.precise = [], this.byWord = [];
    for (let t5 = 0; t5 < e4.length; ) {
      let i9 = he(e4, t5), o4 = be(i9);
      this.chars.push(i9);
      let s99 = e4.slice(t5, t5 + o4), l11 = s99.toUpperCase();
      this.folded.push(he(l11 == s99 ? s99.toLowerCase() : l11, 0)), t5 += o4;
    }
    this.astral = e4.length != this.chars.length;
  }
  match(e4) {
    if (this.pattern.length == 0) return [
      0
    ];
    if (e4.length < this.pattern.length) return null;
    let { chars: t5, folded: i9, any: o4, precise: s99, byWord: l11 } = this;
    if (t5.length == 1) {
      let h3 = he(e4, 0);
      return h3 == t5[0] ? [
        0,
        0,
        be(h3)
      ] : h3 == i9[0] ? [
        -200,
        0,
        be(h3)
      ] : null;
    }
    let r2 = e4.indexOf(this.pattern);
    if (r2 == 0) return [
      0,
      0,
      this.pattern.length
    ];
    let c4 = t5.length, a2 = 0;
    if (r2 < 0) {
      for (let h3 = 0, q13 = Math.min(e4.length, 200); h3 < q13 && a2 < c4; ) {
        let I13 = he(e4, h3);
        (I13 == t5[a2] || I13 == i9[a2]) && (o4[a2++] = h3), h3 += be(I13);
      }
      if (a2 < c4) return null;
    }
    let f2 = 0, u5 = 0, $9 = false, w11 = 0, F13 = -1, W12 = -1, $e7 = /[a-z]/.test(e4), N14 = true;
    for (let h3 = 0, q13 = Math.min(e4.length, 200), I13 = 0; h3 < q13 && u5 < c4; ) {
      let d5 = he(e4, h3);
      r2 < 0 && (f2 < c4 && d5 == t5[f2] && (s99[f2++] = h3), w11 < c4 && (d5 == t5[w11] || d5 == i9[w11] ? (w11 == 0 && (F13 = h3), W12 = h3 + 1, w11++) : w11 = 0));
      let R12, H10 = d5 < 255 ? d5 >= 48 && d5 <= 57 || d5 >= 97 && d5 <= 122 ? 2 : d5 >= 65 && d5 <= 90 ? 1 : 0 : (R12 = rt(d5)) != R12.toLowerCase() ? 1 : R12 != R12.toUpperCase() ? 2 : 0;
      (!h3 || H10 == 1 && $e7 || I13 == 0 && H10 != 0) && (t5[u5] == d5 || i9[u5] == d5 && ($9 = true) ? l11[u5++] = h3 : l11.length && (N14 = false)), I13 = H10, h3 += be(d5);
    }
    return u5 == c4 && l11[0] == 0 && N14 ? this.result(-100 + ($9 ? -200 : 0), l11, e4) : w11 == c4 && F13 == 0 ? [
      -200 - e4.length,
      0,
      W12
    ] : r2 > -1 ? [
      -700 - e4.length,
      r2,
      r2 + this.pattern.length
    ] : w11 == c4 ? [
      -900 - e4.length,
      F13,
      W12
    ] : u5 == c4 ? this.result(-100 + ($9 ? -200 : 0) + -700 + (N14 ? 0 : -1100), l11, e4) : t5.length == 2 ? null : this.result((o4[0] ? -700 : 0) + -200 + -1100, o4, e4);
  }
  result(e4, t5, i9) {
    let o4 = [
      e4 - i9.length
    ], s99 = 1;
    for (let l11 of t5) {
      let r2 = l11 + (this.astral ? be(he(i9, l11)) : 1);
      s99 > 1 && o4[s99 - 1] == l11 ? o4[s99 - 1] = r2 : (o4[s99++] = l11, o4[s99++] = r2);
    }
    return o4;
  }
};
var C5 = y.define({
  combine(n22) {
    return ht(n22, {
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
      defaultKeymap: (e4, t5) => e4 && t5,
      closeOnBlur: (e4, t5) => e4 && t5,
      icons: (e4, t5) => e4 && t5,
      optionClass: (e4, t5) => (i9) => _e5(e4(i9), t5(i9)),
      addToOptions: (e4, t5) => e4.concat(t5)
    });
  }
});
function _e5(n22, e4) {
  return n22 ? e4 ? n22 + " " + e4 : n22 : e4;
}
function et3(n22) {
  let e4 = n22.addToOptions.slice();
  return n22.icons && e4.push({
    render(t5) {
      let i9 = document.createElement("div");
      return i9.classList.add("cm-completionIcon"), t5.type && i9.classList.add(...t5.type.split(/\s+/g).map((o4) => "cm-completionIcon-" + o4)), i9.setAttribute("aria-hidden", "true"), i9;
    },
    position: 20
  }), e4.push({
    render(t5, i9, o4) {
      let s99 = document.createElement("span");
      s99.className = "cm-completionLabel";
      let { label: l11 } = t5, r2 = 0;
      for (let c4 = 1; c4 < o4.length; ) {
        let a2 = o4[c4++], f2 = o4[c4++];
        a2 > r2 && s99.appendChild(document.createTextNode(l11.slice(r2, a2)));
        let u5 = s99.appendChild(document.createElement("span"));
        u5.appendChild(document.createTextNode(l11.slice(a2, f2))), u5.className = "cm-completionMatchedText", r2 = f2;
      }
      return r2 < l11.length && s99.appendChild(document.createTextNode(l11.slice(r2))), s99;
    },
    position: 50
  }, {
    render(t5) {
      if (!t5.detail) return null;
      let i9 = document.createElement("span");
      return i9.className = "cm-completionDetail", i9.textContent = t5.detail, i9;
    },
    position: 80
  }), e4.sort((t5, i9) => t5.position - i9.position).map((t5) => t5.render);
}
function pe4(n22, e4, t5) {
  if (n22 <= t5) return {
    from: 0,
    to: n22
  };
  if (e4 <= n22 >> 1) {
    let o4 = Math.floor(e4 / t5);
    return {
      from: o4 * t5,
      to: (o4 + 1) * t5
    };
  }
  let i9 = Math.floor((n22 - e4) / t5);
  return {
    from: n22 - (i9 + 1) * t5,
    to: n22 - i9 * t5
  };
}
var X6 = class {
  constructor(e4, t5) {
    this.view = e4, this.stateField = t5, this.info = null, this.placeInfo = {
      read: () => this.measureInfo(),
      write: (r2) => this.positionInfo(r2),
      key: this
    };
    let i9 = e4.state.field(t5), { options: o4, selected: s99 } = i9.open, l11 = e4.state.facet(C5);
    this.optionContent = et3(l11), this.optionClass = l11.optionClass, this.range = pe4(o4.length, s99, l11.maxRenderedOptions), this.dom = document.createElement("div"), this.dom.className = "cm-tooltip-autocomplete", this.dom.addEventListener("mousedown", (r2) => {
      for (let c4 = r2.target, a2; c4 && c4 != this.dom; c4 = c4.parentNode) if (c4.nodeName == "LI" && (a2 = /-(\d+)$/.exec(c4.id)) && +a2[1] < o4.length) {
        Te4(e4, o4[+a2[1]]), r2.preventDefault();
        return;
      }
    }), this.list = this.dom.appendChild(this.createListBox(o4, i9.id, this.range)), this.list.addEventListener("scroll", () => {
      this.info && this.view.requestMeasure(this.placeInfo);
    });
  }
  mount() {
    this.updateSel();
  }
  update(e4) {
    e4.state.field(this.stateField) != e4.startState.field(this.stateField) && this.updateSel();
  }
  positioned() {
    this.info && this.view.requestMeasure(this.placeInfo);
  }
  updateSel() {
    let e4 = this.view.state.field(this.stateField), t5 = e4.open;
    if ((t5.selected < this.range.from || t5.selected >= this.range.to) && (this.range = pe4(t5.options.length, t5.selected, this.view.state.facet(C5).maxRenderedOptions), this.list.remove(), this.list = this.dom.appendChild(this.createListBox(t5.options, e4.id, this.range)), this.list.addEventListener("scroll", () => {
      this.info && this.view.requestMeasure(this.placeInfo);
    })), this.updateSelectedOption(t5.selected)) {
      this.info && (this.info.remove(), this.info = null);
      let { completion: i9 } = t5.options[t5.selected], { info: o4 } = i9;
      if (!o4) return;
      let s99 = typeof o4 == "string" ? document.createTextNode(o4) : o4(i9);
      if (!s99) return;
      "then" in s99 ? s99.then((l11) => {
        l11 && this.view.state.field(this.stateField, false) == e4 && this.addInfoPane(l11);
      }).catch((l11) => Z2(this.view.state, l11, "completion info")) : this.addInfoPane(s99);
    }
  }
  addInfoPane(e4) {
    let t5 = this.info = document.createElement("div");
    t5.className = "cm-tooltip cm-completionInfo", t5.appendChild(e4), this.dom.appendChild(t5), this.view.requestMeasure(this.placeInfo);
  }
  updateSelectedOption(e4) {
    let t5 = null;
    for (let i9 = this.list.firstChild, o4 = this.range.from; i9; i9 = i9.nextSibling, o4++) o4 == e4 ? i9.hasAttribute("aria-selected") || (i9.setAttribute("aria-selected", "true"), t5 = i9) : i9.hasAttribute("aria-selected") && i9.removeAttribute("aria-selected");
    return t5 && nt2(this.list, t5), t5;
  }
  measureInfo() {
    let e4 = this.dom.querySelector("[aria-selected]");
    if (!e4 || !this.info) return null;
    let t5 = this.dom.getBoundingClientRect(), i9 = this.info.getBoundingClientRect(), o4 = e4.getBoundingClientRect();
    if (o4.top > Math.min(innerHeight, t5.bottom) - 10 || o4.bottom < Math.max(0, t5.top) + 10) return null;
    let s99 = Math.max(0, Math.min(o4.top, innerHeight - i9.height)) - t5.top, l11 = this.view.textDirection == O2.RTL, r2 = t5.left, c4 = innerWidth - t5.right;
    return l11 && r2 < Math.min(i9.width, c4) ? l11 = false : !l11 && c4 < Math.min(i9.width, r2) && (l11 = true), {
      top: s99,
      left: l11
    };
  }
  positionInfo(e4) {
    this.info && (this.info.style.top = (e4 ? e4.top : -1e6) + "px", e4 && (this.info.classList.toggle("cm-completionInfo-left", e4.left), this.info.classList.toggle("cm-completionInfo-right", !e4.left)));
  }
  createListBox(e4, t5, i9) {
    let o4 = document.createElement("ul");
    o4.id = t5, o4.setAttribute("role", "listbox"), o4.setAttribute("aria-expanded", "true"), o4.setAttribute("aria-label", this.view.state.phrase("Completions"));
    for (let s99 = i9.from; s99 < i9.to; s99++) {
      let { completion: l11, match: r2 } = e4[s99], c4 = o4.appendChild(document.createElement("li"));
      c4.id = t5 + "-" + s99, c4.setAttribute("role", "option");
      let a2 = this.optionClass(l11);
      a2 && (c4.className = a2);
      for (let f2 of this.optionContent) {
        let u5 = f2(l11, this.view.state, r2);
        u5 && c4.appendChild(u5);
      }
    }
    return i9.from && o4.classList.add("cm-completionListIncompleteTop"), i9.to < e4.length && o4.classList.add("cm-completionListIncompleteBottom"), o4;
  }
};
function tt4(n22) {
  return (e4) => new X6(e4, n22);
}
function nt2(n22, e4) {
  let t5 = n22.getBoundingClientRect(), i9 = e4.getBoundingClientRect();
  i9.top < t5.top ? n22.scrollTop -= t5.top - i9.top : i9.bottom > t5.bottom && (n22.scrollTop += i9.bottom - t5.bottom);
}
function de4(n22) {
  return (n22.boost || 0) * 100 + (n22.apply ? 10 : 0) + (n22.info ? 5 : 0) + (n22.type ? 1 : 0);
}
function it3(n22, e4) {
  let t5 = [], i9 = 0;
  for (let l11 of n22) if (l11.hasResult()) if (l11.result.filter === false) {
    let r2 = l11.result.getMatch;
    for (let c4 of l11.result.options) {
      let a2 = [
        1e9 - i9++
      ];
      if (r2) for (let f2 of r2(c4)) a2.push(f2);
      t5.push(new B5(c4, l11, a2));
    }
  } else {
    let r2 = new Q6(e4.sliceDoc(l11.from, l11.to)), c4;
    for (let a2 of l11.result.options) (c4 = r2.match(a2.label)) && (a2.boost != null && (c4[0] += a2.boost), t5.push(new B5(a2, l11, c4)));
  }
  let o4 = [], s99 = null;
  for (let l11 of t5.sort(rt3)) !s99 || s99.label != l11.completion.label || s99.detail != l11.completion.detail || s99.type != null && l11.completion.type != null && s99.type != l11.completion.type || s99.apply != l11.completion.apply ? o4.push(l11) : de4(l11.completion) > de4(s99) && (o4[o4.length - 1] = l11), s99 = l11.completion;
  return o4;
}
var Y4 = class n6 {
  constructor(e4, t5, i9, o4, s99) {
    this.options = e4, this.attrs = t5, this.tooltip = i9, this.timestamp = o4, this.selected = s99;
  }
  setSelected(e4, t5) {
    return e4 == this.selected || e4 >= this.options.length ? this : new n6(this.options, me5(t5, e4), this.tooltip, this.timestamp, e4);
  }
  static build(e4, t5, i9, o4, s99) {
    let l11 = it3(e4, t5);
    if (!l11.length) return null;
    let r2 = 0;
    if (o4 && o4.selected) {
      let c4 = o4.options[o4.selected].completion;
      for (let a2 = 0; a2 < l11.length; a2++) if (l11[a2].completion == c4) {
        r2 = a2;
        break;
      }
    }
    return new n6(l11, me5(i9, r2), {
      pos: e4.reduce((c4, a2) => a2.hasResult() ? Math.min(c4, a2.from) : c4, 1e8),
      create: tt4(p),
      above: s99.aboveCursor
    }, o4 ? o4.timestamp : Date.now(), r2);
  }
  map(e4) {
    return new n6(this.options, this.attrs, Object.assign(Object.assign({}, this.tooltip), {
      pos: e4.mapPos(this.tooltip.pos)
    }), this.timestamp, this.selected);
  }
};
var G2 = class n7 {
  constructor(e4, t5, i9) {
    this.active = e4, this.id = t5, this.open = i9;
  }
  static start() {
    return new n7(lt2, "cm-ac-" + Math.floor(Math.random() * 2e6).toString(36), null);
  }
  update(e4) {
    let { state: t5 } = e4, i9 = t5.facet(C5), s99 = (i9.override || t5.languageDataAt("autocomplete", x4(t5)).map(Ze3)).map((r2) => (this.active.find((a2) => a2.source == r2) || new v2(r2, this.active.some((a2) => a2.state != 0) ? 1 : 0)).update(e4, i9));
    s99.length == this.active.length && s99.every((r2, c4) => r2 == this.active[c4]) && (s99 = this.active);
    let l11 = e4.selection || s99.some((r2) => r2.hasResult() && e4.changes.touchesRange(r2.from, r2.to)) || !ot4(s99, this.active) ? Y4.build(s99, t5, this.id, this.open, i9) : this.open && e4.docChanged ? this.open.map(e4.changes) : this.open;
    !l11 && s99.every((r2) => r2.state != 1) && s99.some((r2) => r2.hasResult()) && (s99 = s99.map((r2) => r2.hasResult() ? new v2(r2.source, 0) : r2));
    for (let r2 of e4.effects) r2.is(se5) && (l11 = l11 && l11.setSelected(r2.value, this.id));
    return s99 == this.active && l11 == this.open ? this : new n7(s99, this.id, l11);
  }
  get tooltip() {
    return this.open ? this.open.tooltip : null;
  }
  get attrs() {
    return this.open ? this.open.attrs : st2;
  }
};
function ot4(n22, e4) {
  if (n22 == e4) return true;
  for (let t5 = 0, i9 = 0; ; ) {
    for (; t5 < n22.length && !n22[t5].hasResult; ) t5++;
    for (; i9 < e4.length && !e4[i9].hasResult; ) i9++;
    let o4 = t5 == n22.length, s99 = i9 == e4.length;
    if (o4 || s99) return o4 == s99;
    if (n22[t5++].result != e4[i9++].result) return false;
  }
}
var st2 = {
  "aria-autocomplete": "list"
};
function me5(n22, e4) {
  return {
    "aria-autocomplete": "list",
    "aria-haspopup": "listbox",
    "aria-activedescendant": n22 + "-" + e4,
    "aria-controls": n22
  };
}
var lt2 = [];
function rt3(n22, e4) {
  let t5 = e4.match[0] - n22.match[0];
  return t5 || n22.completion.label.localeCompare(e4.completion.label);
}
function J3(n22) {
  return n22.isUserEvent("input.type") ? "input" : n22.isUserEvent("delete.backward") ? "delete" : null;
}
var v2 = class n8 {
  constructor(e4, t5, i9 = -1) {
    this.source = e4, this.state = t5, this.explicitPos = i9;
  }
  hasResult() {
    return false;
  }
  update(e4, t5) {
    let i9 = J3(e4), o4 = this;
    i9 ? o4 = o4.handleUserEvent(e4, i9, t5) : e4.docChanged ? o4 = o4.handleChange(e4) : e4.selection && o4.state != 0 && (o4 = new n8(o4.source, 0));
    for (let s99 of e4.effects) if (s99.is(oe4)) o4 = new n8(o4.source, 1, s99.value ? x4(e4.state) : -1);
    else if (s99.is(k3)) o4 = new n8(o4.source, 0);
    else if (s99.is(Oe4)) for (let l11 of s99.value) l11.source == o4.source && (o4 = l11);
    return o4;
  }
  handleUserEvent(e4, t5, i9) {
    return t5 == "delete" || !i9.activateOnTyping ? this.map(e4.changes) : new n8(this.source, 1);
  }
  handleChange(e4) {
    return e4.changes.touchesRange(x4(e4.startState)) ? new n8(this.source, 0) : this.map(e4.changes);
  }
  map(e4) {
    return e4.empty || this.explicitPos < 0 ? this : new n8(this.source, this.state, e4.mapPos(this.explicitPos));
  }
};
var Z6 = class n9 extends v2 {
  constructor(e4, t5, i9, o4, s99) {
    super(e4, 2, t5), this.result = i9, this.from = o4, this.to = s99;
  }
  hasResult() {
    return true;
  }
  handleUserEvent(e4, t5, i9) {
    var o4;
    let s99 = e4.changes.mapPos(this.from), l11 = e4.changes.mapPos(this.to, 1), r2 = x4(e4.state);
    if ((this.explicitPos < 0 ? r2 <= s99 : r2 < this.from) || r2 > l11 || t5 == "delete" && x4(e4.startState) == this.from) return new v2(this.source, t5 == "input" && i9.activateOnTyping ? 1 : 0);
    let c4 = this.explicitPos < 0 ? -1 : e4.changes.mapPos(this.explicitPos), a2;
    return ct2(this.result.validFor, e4.state, s99, l11) ? new n9(this.source, c4, this.result, s99, l11) : this.result.update && (a2 = this.result.update(this.result, s99, l11, new M5(e4.state, r2, c4 >= 0))) ? new n9(this.source, c4, a2, a2.from, (o4 = a2.to) !== null && o4 !== void 0 ? o4 : x4(e4.state)) : new v2(this.source, 1, c4);
  }
  handleChange(e4) {
    return e4.changes.touchesRange(this.from, this.to) ? new v2(this.source, 0) : this.map(e4.changes);
  }
  map(e4) {
    return e4.empty ? this : new n9(this.source, this.explicitPos < 0 ? -1 : e4.mapPos(this.explicitPos), this.result, e4.mapPos(this.from), e4.mapPos(this.to, 1));
  }
};
function ct2(n22, e4, t5, i9) {
  if (!n22) return false;
  let o4 = e4.sliceDoc(t5, i9);
  return typeof n22 == "function" ? n22(o4, t5, i9, e4) : Pe4(n22, true).test(o4);
}
var oe4 = v.define();
var k3 = v.define();
var Oe4 = v.define({
  map(n22, e4) {
    return n22.map((t5) => t5.map(e4));
  }
});
var se5 = v.define();
var p = $.define({
  create() {
    return G2.start();
  },
  update(n22, e4) {
    return n22.update(e4);
  },
  provide: (n22) => [
    rn.from(n22, (e4) => e4.tooltip),
    M2.contentAttributes.from(n22, (e4) => e4.attrs)
  ]
});
var Re3 = 75;
function L4(n22, e4 = "option") {
  return (t5) => {
    let i9 = t5.state.field(p, false);
    if (!i9 || !i9.open || Date.now() - i9.open.timestamp < Re3) return false;
    let o4 = 1, s99;
    e4 == "page" && (s99 = ho(t5, i9.open.tooltip)) && (o4 = Math.max(2, Math.floor(s99.dom.offsetHeight / s99.dom.querySelector("li").offsetHeight) - 1));
    let l11 = i9.open.selected + o4 * (n22 ? 1 : -1), { length: r2 } = i9.open.options;
    return l11 < 0 ? l11 = e4 == "page" ? 0 : r2 - 1 : l11 >= r2 && (l11 = e4 == "page" ? r2 - 1 : 0), t5.dispatch({
      effects: se5.of(l11)
    }), true;
  };
}
var at4 = (n22) => {
  let e4 = n22.state.field(p, false);
  return n22.state.readOnly || !e4 || !e4.open || Date.now() - e4.open.timestamp < Re3 ? false : (Te4(n22, e4.open.options[e4.open.selected]), true);
};
var ft3 = (n22) => n22.state.field(p, false) ? (n22.dispatch({
  effects: oe4.of(true)
}), true) : false;
var ut = (n22) => {
  let e4 = n22.state.field(p, false);
  return !e4 || !e4.active.some((t5) => t5.state != 0) ? false : (n22.dispatch({
    effects: k3.of(null)
  }), true);
};
var _4 = class {
  constructor(e4, t5) {
    this.active = e4, this.context = t5, this.time = Date.now(), this.updates = [], this.done = void 0;
  }
};
var ge5 = 50;
var ht3 = 50;
var pt2 = 1e3;
var dt = P2.fromClass(class {
  constructor(n22) {
    this.view = n22, this.debounceUpdate = -1, this.running = [], this.debounceAccept = -1, this.composing = 0;
    for (let e4 of n22.state.field(p).active) e4.state == 1 && this.startQuery(e4);
  }
  update(n22) {
    let e4 = n22.state.field(p);
    if (!n22.selectionSet && !n22.docChanged && n22.startState.field(p) == e4) return;
    let t5 = n22.transactions.some((i9) => (i9.selection || i9.docChanged) && !J3(i9));
    for (let i9 = 0; i9 < this.running.length; i9++) {
      let o4 = this.running[i9];
      if (t5 || o4.updates.length + n22.transactions.length > ht3 && Date.now() - o4.time > pt2) {
        for (let s99 of o4.context.abortListeners) try {
          s99();
        } catch (l11) {
          Z2(this.view.state, l11);
        }
        o4.context.abortListeners = null, this.running.splice(i9--, 1);
      } else o4.updates.push(...n22.transactions);
    }
    if (this.debounceUpdate > -1 && clearTimeout(this.debounceUpdate), this.debounceUpdate = e4.active.some((i9) => i9.state == 1 && !this.running.some((o4) => o4.active.source == i9.source)) ? setTimeout(() => this.startUpdate(), ge5) : -1, this.composing != 0) for (let i9 of n22.transactions) J3(i9) == "input" ? this.composing = 2 : this.composing == 2 && i9.selection && (this.composing = 3);
  }
  startUpdate() {
    this.debounceUpdate = -1;
    let { state: n22 } = this.view, e4 = n22.field(p);
    for (let t5 of e4.active) t5.state == 1 && !this.running.some((i9) => i9.active.source == t5.source) && this.startQuery(t5);
  }
  startQuery(n22) {
    let { state: e4 } = this.view, t5 = x4(e4), i9 = new M5(e4, t5, n22.explicitPos == t5), o4 = new _4(n22, i9);
    this.running.push(o4), Promise.resolve(n22.source(i9)).then((s99) => {
      o4.context.aborted || (o4.done = s99 || null, this.scheduleAccept());
    }, (s99) => {
      this.view.dispatch({
        effects: k3.of(null)
      }), Z2(this.view.state, s99);
    });
  }
  scheduleAccept() {
    this.running.every((n22) => n22.done !== void 0) ? this.accept() : this.debounceAccept < 0 && (this.debounceAccept = setTimeout(() => this.accept(), ge5));
  }
  accept() {
    var n22;
    this.debounceAccept > -1 && clearTimeout(this.debounceAccept), this.debounceAccept = -1;
    let e4 = [], t5 = this.view.state.facet(C5);
    for (let i9 = 0; i9 < this.running.length; i9++) {
      let o4 = this.running[i9];
      if (o4.done === void 0) continue;
      if (this.running.splice(i9--, 1), o4.done) {
        let l11 = new Z6(o4.active.source, o4.active.explicitPos, o4.done, o4.done.from, (n22 = o4.done.to) !== null && n22 !== void 0 ? n22 : x4(o4.updates.length ? o4.updates[0].startState : this.view.state));
        for (let r2 of o4.updates) l11 = l11.update(r2, t5);
        if (l11.hasResult()) {
          e4.push(l11);
          continue;
        }
      }
      let s99 = this.view.state.field(p).active.find((l11) => l11.source == o4.active.source);
      if (s99 && s99.state == 1) if (o4.done == null) {
        let l11 = new v2(o4.active.source, 0);
        for (let r2 of o4.updates) l11 = l11.update(r2, t5);
        l11.state != 1 && e4.push(l11);
      } else this.startQuery(s99);
    }
    e4.length && this.view.dispatch({
      effects: Oe4.of(e4)
    });
  }
}, {
  eventHandlers: {
    blur() {
      let n22 = this.view.state.field(p, false);
      n22 && n22.tooltip && this.view.state.facet(C5).closeOnBlur && this.view.dispatch({
        effects: k3.of(null)
      });
    },
    compositionstart() {
      this.composing = 1;
    },
    compositionend() {
      this.composing == 3 && setTimeout(() => this.view.dispatch({
        effects: oe4.of(false)
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
      let n22 = document.createElement("span");
      return n22.className = "cm-snippetFieldPosition", n22;
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
  constructor(e4, t5) {
    this.ranges = e4, this.active = t5, this.deco = C2.set(e4.map((i9) => (i9.from == i9.to ? mt2 : gt).range(i9.from, i9.to)));
  }
  map(e4) {
    let t5 = [];
    for (let i9 of this.ranges) {
      let o4 = i9.map(e4);
      if (!o4) return null;
      t5.push(o4);
    }
    return new n10(t5, this.active);
  }
  selectionInsideField(e4) {
    return e4.ranges.every((t5) => this.ranges.some((i9) => i9.field == this.active && i9.from <= t5.from && i9.to >= t5.to));
  }
};
var O4 = v.define({
  map(n22, e4) {
    return n22 && n22.map(e4);
  }
});
var bt2 = v.define();
var E3 = $.define({
  create() {
    return null;
  },
  update(n22, e4) {
    for (let t5 of e4.effects) {
      if (t5.is(O4)) return t5.value;
      if (t5.is(bt2) && n22) return new A5(n22.ranges, t5.value);
    }
    return n22 && e4.docChanged && (n22 = n22.map(e4.changes)), n22 && e4.selection && !n22.selectionInsideField(e4.selection) && (n22 = null), n22;
  },
  provide: (n22) => M2.decorations.from(n22, (e4) => e4 ? e4.deco : C2.none)
});
function le3(n22, e4) {
  return x.create(n22.filter((t5) => t5.field == e4).map((t5) => x.range(t5.from, t5.to)));
}
function Me3(n22) {
  return ({ state: e4, dispatch: t5 }) => {
    let i9 = e4.field(E3, false);
    if (!i9 || n22 < 0 && i9.active == 0) return false;
    let o4 = i9.active + n22, s99 = n22 > 0 && !i9.ranges.some((l11) => l11.field == o4 + n22);
    return t5(e4.update({
      selection: le3(i9.ranges, o4),
      effects: O4.of(s99 ? null : new A5(i9.ranges, o4))
    })), true;
  };
}
var yt2 = ({ state: n22, dispatch: e4 }) => n22.field(E3, false) ? (e4(n22.update({
  effects: O4.of(null)
})), true) : false;
var wt2 = Me3(1);
var xt3 = Me3(-1);
var Ct3 = [
  {
    key: "Tab",
    run: wt2,
    shift: xt3
  },
  {
    key: "Escape",
    run: yt2
  }
];
var be4 = y.define({
  combine(n22) {
    return n22.length ? n22[0] : Ct3;
  }
});
var St2 = lt.highest(ur.compute([
  be4
], (n22) => n22.facet(be4)));
var It3 = M2.domEventHandlers({
  mousedown(n22, e4) {
    let t5 = e4.state.field(E3, false), i9;
    if (!t5 || (i9 = e4.posAtCoords({
      x: n22.clientX,
      y: n22.clientY
    })) == null) return false;
    let o4 = t5.ranges.find((s99) => s99.from <= i9 && s99.to >= i9);
    return !o4 || o4.field == t5.active ? false : (e4.dispatch({
      selection: le3(t5.ranges, o4.field),
      effects: O4.of(t5.ranges.some((s99) => s99.field > o4.field) ? new A5(t5.ranges, o4.field) : null)
    }), true);
  }
});
var D4 = {
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
  map(n22, e4) {
    let t5 = e4.mapPos(n22, -1, b.TrackAfter);
    return t5 ?? void 0;
  }
});
var re4 = v.define({
  map(n22, e4) {
    return e4.mapPos(n22);
  }
});
var ce5 = new class extends z {
}();
ce5.startSide = 1;
ce5.endSide = -1;
var ke5 = $.define({
  create() {
    return O.empty;
  },
  update(n22, e4) {
    if (e4.selection) {
      let t5 = e4.state.doc.lineAt(e4.selection.main.head).from, i9 = e4.startState.doc.lineAt(e4.startState.selection.main.head).from;
      t5 != e4.changes.mapPos(i9, -1) && (n22 = O.empty);
    }
    n22 = n22.map(e4.changes);
    for (let t5 of e4.effects) t5.is(S5) ? n22 = n22.update({
      add: [
        ce5.range(t5.value, t5.value + 1)
      ]
    }) : t5.is(re4) && (n22 = n22.update({
      filter: (i9) => i9 != t5.value
    }));
    return n22;
  }
});
function zt() {
  return [
    Tt3,
    ke5
  ];
}
var V6 = "()[]{}<>";
function De4(n22) {
  for (let e4 = 0; e4 < V6.length; e4 += 2) if (V6.charCodeAt(e4) == n22) return V6.charAt(e4 + 1);
  return rt(n22 < 128 ? n22 : n22 + 1);
}
function je3(n22, e4) {
  return n22.languageDataAt("closeBrackets", e4)[0] || D4;
}
var Pt3 = typeof navigator == "object" && /Android\b/.test(navigator.userAgent);
var Tt3 = M2.inputHandler.of((n22, e4, t5, i9) => {
  if ((Pt3 ? n22.composing : n22.compositionStarted) || n22.state.readOnly) return false;
  let o4 = n22.state.selection.main;
  if (i9.length > 2 || i9.length == 2 && be(he(i9, 0)) == 1 || e4 != o4.from || t5 != o4.to) return false;
  let s99 = Rt2(n22.state, i9);
  return s99 ? (n22.dispatch(s99), true) : false;
});
var Ot3 = ({ state: n22, dispatch: e4 }) => {
  if (n22.readOnly) return false;
  let i9 = je3(n22, n22.selection.main.head).brackets || D4.brackets, o4 = null, s99 = n22.changeByRange((l11) => {
    if (l11.empty) {
      let r2 = Lt3(n22.doc, l11.head);
      for (let c4 of i9) if (c4 == r2 && U5(n22.doc, l11.head) == De4(he(c4, 0))) return {
        changes: {
          from: l11.head - c4.length,
          to: l11.head + c4.length
        },
        range: x.cursor(l11.head - c4.length),
        userEvent: "delete.backward"
      };
    }
    return {
      range: o4 = l11
    };
  });
  return o4 || e4(n22.update(s99, {
    scrollIntoView: true
  })), !o4;
};
var Qt2 = [
  {
    key: "Backspace",
    run: Ot3
  }
];
function Rt2(n22, e4) {
  let t5 = je3(n22, n22.selection.main.head), i9 = t5.brackets || D4.brackets;
  for (let o4 of i9) {
    let s99 = De4(he(o4, 0));
    if (e4 == o4) return s99 == o4 ? kt2(n22, o4, i9.indexOf(o4 + o4 + o4) > -1) : Mt3(n22, o4, s99, t5.before || D4.before);
    if (e4 == s99 && Ue3(n22, n22.selection.main.from)) return Bt3(n22, o4, s99);
  }
  return null;
}
function Ue3(n22, e4) {
  let t5 = false;
  return n22.field(ke5).between(0, n22.doc.length, (i9) => {
    i9 == e4 && (t5 = true);
  }), t5;
}
function U5(n22, e4) {
  let t5 = n22.sliceString(e4, e4 + 2);
  return t5.slice(0, be(he(t5, 0)));
}
function Lt3(n22, e4) {
  let t5 = n22.sliceString(e4 - 2, e4);
  return be(he(t5, 0)) == t5.length ? t5 : t5.slice(1);
}
function Mt3(n22, e4, t5, i9) {
  let o4 = null, s99 = n22.changeByRange((l11) => {
    if (!l11.empty) return {
      changes: [
        {
          insert: e4,
          from: l11.from
        },
        {
          insert: t5,
          from: l11.to
        }
      ],
      effects: S5.of(l11.to + e4.length),
      range: x.range(l11.anchor + e4.length, l11.head + e4.length)
    };
    let r2 = U5(n22.doc, l11.head);
    return !r2 || /\s/.test(r2) || i9.indexOf(r2) > -1 ? {
      changes: {
        insert: e4 + t5,
        from: l11.head
      },
      effects: S5.of(l11.head + e4.length),
      range: x.cursor(l11.head + e4.length)
    } : {
      range: o4 = l11
    };
  });
  return o4 ? null : n22.update(s99, {
    scrollIntoView: true,
    userEvent: "input.type"
  });
}
function Bt3(n22, e4, t5) {
  let i9 = null, o4 = n22.selection.ranges.map((s99) => s99.empty && U5(n22.doc, s99.head) == t5 ? x.cursor(s99.head + t5.length) : i9 = s99);
  return i9 ? null : n22.update({
    selection: x.create(o4, n22.selection.mainIndex),
    scrollIntoView: true,
    effects: n22.selection.ranges.map(({ from: s99 }) => re4.of(s99))
  });
}
function kt2(n22, e4, t5) {
  let i9 = null, o4 = n22.changeByRange((s99) => {
    if (!s99.empty) return {
      changes: [
        {
          insert: e4,
          from: s99.from
        },
        {
          insert: e4,
          from: s99.to
        }
      ],
      effects: S5.of(s99.to + e4.length),
      range: x.range(s99.anchor + e4.length, s99.head + e4.length)
    };
    let l11 = s99.head, r2 = U5(n22.doc, l11);
    if (r2 == e4) {
      if (xe4(n22, l11)) return {
        changes: {
          insert: e4 + e4,
          from: l11
        },
        effects: S5.of(l11 + e4.length),
        range: x.cursor(l11 + e4.length)
      };
      if (Ue3(n22, l11)) {
        let c4 = t5 && n22.sliceDoc(l11, l11 + e4.length * 3) == e4 + e4 + e4;
        return {
          range: x.cursor(l11 + e4.length * (c4 ? 3 : 1)),
          effects: re4.of(l11)
        };
      }
    } else {
      if (t5 && n22.sliceDoc(l11 - 2 * e4.length, l11) == e4 + e4 && xe4(n22, l11 - 2 * e4.length)) return {
        changes: {
          insert: e4 + e4 + e4 + e4,
          from: l11
        },
        effects: S5.of(l11 + e4.length),
        range: x.cursor(l11 + e4.length)
      };
      if (n22.charCategorizer(l11)(r2) != E.Word) {
        let c4 = n22.sliceDoc(l11 - 1, l11);
        if (c4 != e4 && n22.charCategorizer(l11)(c4) != E.Word && !Dt3(n22, l11, e4)) return {
          changes: {
            insert: e4 + e4,
            from: l11
          },
          effects: S5.of(l11 + e4.length),
          range: x.cursor(l11 + e4.length)
        };
      }
    }
    return {
      range: i9 = s99
    };
  });
  return i9 ? null : n22.update(o4, {
    scrollIntoView: true,
    userEvent: "input.type"
  });
}
function xe4(n22, e4) {
  let t5 = m3(n22).resolveInner(e4 + 1);
  return t5.parent && t5.from == e4;
}
function Dt3(n22, e4, t5) {
  let i9 = m3(n22).resolveInner(e4, -1);
  for (let o4 = 0; o4 < 5; o4++) {
    if (n22.sliceDoc(i9.from, i9.from + t5.length) == t5) return true;
    let s99 = i9.to == e4 && i9.parent;
    if (!s99) break;
    i9 = s99;
  }
  return false;
}
function Xt2(n22 = {}) {
  return [
    p,
    C5.of(n22),
    dt,
    Ut2,
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
var Ut2 = lt.highest(ur.computeN([
  C5
], (n22) => n22.facet(C5).defaultKeymap ? [
  jt3
] : []));

// deno:https://esm.sh/@codemirror/commands@0.20.0/denonext/commands.mjs
var ot5 = (e4) => {
  let t5 = j4(e4.state);
  return t5.line ? lt3(e4) : t5.block ? st3(e4) : false;
};
function C6(e4, t5) {
  return ({ state: r2, dispatch: n22 }) => {
    if (r2.readOnly) return false;
    let l11 = e4(t5, r2);
    return l11 ? (n22(r2.update(l11)), true) : false;
  };
}
var lt3 = C6(ee4, 0);
var on2 = C6(ee4, 1);
var ln2 = C6(ee4, 2);
var ct3 = C6(w5, 0);
var cn = C6(w5, 1);
var sn3 = C6(w5, 2);
var st3 = C6((e4, t5) => w5(e4, t5, ut2(t5)), 0);
function j4(e4, t5 = e4.selection.main.head) {
  let r2 = e4.languageDataAt("commentTokens", t5);
  return r2.length ? r2[0] : {};
}
var M6 = 50;
function it4(e4, { open: t5, close: r2 }, n22, l11) {
  let o4 = e4.sliceDoc(n22 - M6, n22), c4 = e4.sliceDoc(l11, l11 + M6), s99 = /\s*$/.exec(o4)[0].length, i9 = /^\s*/.exec(c4)[0].length, u5 = o4.length - s99;
  if (o4.slice(u5 - t5.length, u5) == t5 && c4.slice(i9, i9 + r2.length) == r2) return {
    open: {
      pos: n22 - s99,
      margin: s99 && 1
    },
    close: {
      pos: l11 + i9,
      margin: i9 && 1
    }
  };
  let f2, a2;
  l11 - n22 <= 2 * M6 ? f2 = a2 = e4.sliceDoc(n22, l11) : (f2 = e4.sliceDoc(n22, n22 + M6), a2 = e4.sliceDoc(l11 - M6, l11));
  let d5 = /^\s*/.exec(f2)[0].length, S11 = /\s*$/.exec(a2)[0].length, L10 = a2.length - S11 - r2.length;
  return f2.slice(d5, d5 + t5.length) == t5 && a2.slice(L10, L10 + r2.length) == r2 ? {
    open: {
      pos: n22 + d5 + t5.length,
      margin: /\s/.test(f2.charAt(d5 + t5.length)) ? 1 : 0
    },
    close: {
      pos: l11 - S11 - r2.length,
      margin: /\s/.test(a2.charAt(L10 - 1)) ? 1 : 0
    }
  } : null;
}
function ut2(e4) {
  let t5 = [];
  for (let r2 of e4.selection.ranges) {
    let n22 = e4.doc.lineAt(r2.from), l11 = r2.to <= n22.to ? n22 : e4.doc.lineAt(r2.to), o4 = t5.length - 1;
    o4 >= 0 && t5[o4].to > n22.from ? t5[o4].to = l11.to : t5.push({
      from: n22.from,
      to: l11.to
    });
  }
  return t5;
}
function w5(e4, t5, r2 = t5.selection.ranges) {
  let n22 = r2.map((o4) => j4(t5, o4.from).block);
  if (!n22.every((o4) => o4)) return null;
  let l11 = r2.map((o4, c4) => it4(t5, n22[c4], o4.from, o4.to));
  if (e4 != 2 && !l11.every((o4) => o4)) return {
    changes: t5.changes(r2.map((o4, c4) => l11[c4] ? [] : [
      {
        from: o4.from,
        insert: n22[c4].open + " "
      },
      {
        from: o4.to,
        insert: " " + n22[c4].close
      }
    ]))
  };
  if (e4 != 1 && l11.some((o4) => o4)) {
    let o4 = [];
    for (let c4 = 0, s99; c4 < l11.length; c4++) if (s99 = l11[c4]) {
      let i9 = n22[c4], { open: u5, close: f2 } = s99;
      o4.push({
        from: u5.pos - i9.open.length,
        to: u5.pos + u5.margin
      }, {
        from: f2.pos - f2.margin,
        to: f2.pos + i9.close.length
      });
    }
    return {
      changes: o4
    };
  }
  return null;
}
function ee4(e4, t5, r2 = t5.selection.ranges) {
  let n22 = [], l11 = -1;
  for (let { from: o4, to: c4 } of r2) {
    let s99 = n22.length, i9 = 1e9;
    for (let u5 = o4; u5 <= c4; ) {
      let f2 = t5.doc.lineAt(u5);
      if (f2.from > l11 && (o4 == c4 || c4 > f2.from)) {
        l11 = f2.from;
        let a2 = j4(t5, u5).line;
        if (!a2) continue;
        let d5 = /^\s*/.exec(f2.text)[0].length, S11 = d5 == f2.length, L10 = f2.text.slice(d5, d5 + a2.length) == a2 ? d5 : -1;
        d5 < f2.text.length && d5 < i9 && (i9 = d5), n22.push({
          line: f2,
          comment: L10,
          token: a2,
          indent: d5,
          empty: S11,
          single: false
        });
      }
      u5 = f2.to + 1;
    }
    if (i9 < 1e9) for (let u5 = s99; u5 < n22.length; u5++) n22[u5].indent < n22[u5].line.text.length && (n22[u5].indent = i9);
    n22.length == s99 + 1 && (n22[s99].single = true);
  }
  if (e4 != 2 && n22.some((o4) => o4.comment < 0 && (!o4.empty || o4.single))) {
    let o4 = [];
    for (let { line: s99, token: i9, indent: u5, empty: f2, single: a2 } of n22) (a2 || !f2) && o4.push({
      from: s99.from + u5,
      insert: i9 + " "
    });
    let c4 = t5.changes(o4);
    return {
      changes: c4,
      selection: t5.selection.map(c4, 1)
    };
  } else if (e4 != 1 && n22.some((o4) => o4.comment >= 0)) {
    let o4 = [];
    for (let { line: c4, comment: s99, token: i9 } of n22) if (s99 >= 0) {
      let u5 = c4.from + s99, f2 = u5 + i9.length;
      c4.text[f2 - c4.from] == " " && f2++, o4.push({
        from: u5,
        to: f2
      });
    }
    return {
      changes: o4
    };
  }
  return null;
}
var X7 = F.define();
var ft4 = F.define();
var at5 = y.define();
var Se5 = y.define({
  combine(e4) {
    return ht(e4, {
      minDepth: 100,
      newGroupDelay: 500
    }, {
      minDepth: Math.max,
      newGroupDelay: Math.min
    });
  }
});
function ht4(e4) {
  let t5 = 0;
  return e4.iterChangedRanges((r2, n22) => t5 = n22), t5;
}
var v3 = $.define({
  create() {
    return B6.empty;
  },
  update(e4, t5) {
    let r2 = t5.state.facet(Se5), n22 = t5.annotation(X7);
    if (n22) {
      let i9 = t5.docChanged ? x.single(ht4(t5.changes)) : void 0, u5 = g3.fromTransaction(t5, i9), f2 = n22.side, a2 = f2 == 0 ? e4.undone : e4.done;
      return u5 ? a2 = R5(a2, a2.length, r2.minDepth, u5) : a2 = Le5(a2, t5.startState.selection), new B6(f2 == 0 ? n22.rest : a2, f2 == 0 ? a2 : n22.rest);
    }
    let l11 = t5.annotation(ft4);
    if ((l11 == "full" || l11 == "before") && (e4 = e4.isolate()), t5.annotation(S.addToHistory) === false) return t5.changes.empty ? e4 : e4.addMapping(t5.changes.desc);
    let o4 = g3.fromTransaction(t5), c4 = t5.annotation(S.time), s99 = t5.annotation(S.userEvent);
    return o4 ? e4 = e4.addChanges(o4, c4, s99, r2.newGroupDelay, r2.minDepth) : t5.selection && (e4 = e4.addSelection(t5.startState.selection, c4, s99, r2.newGroupDelay)), (l11 == "full" || l11 == "after") && (e4 = e4.isolate()), e4;
  },
  toJSON(e4) {
    return {
      done: e4.done.map((t5) => t5.toJSON()),
      undone: e4.undone.map((t5) => t5.toJSON())
    };
  },
  fromJSON(e4) {
    return new B6(e4.done.map(g3.fromJSON), e4.undone.map(g3.fromJSON));
  }
});
function un(e4 = {}) {
  return [
    v3,
    Se5.of(e4),
    M2.domEventHandlers({
      beforeinput(t5, r2) {
        let n22 = t5.inputType == "historyUndo" ? Be4 : t5.inputType == "historyRedo" ? Ce5 : null;
        return n22 ? (t5.preventDefault(), n22(r2)) : false;
      }
    })
  ];
}
function U6(e4, t5) {
  return function({ state: r2, dispatch: n22 }) {
    if (!t5 && r2.readOnly) return false;
    let l11 = r2.field(v3, false);
    if (!l11) return false;
    let o4 = l11.pop(e4, r2, t5);
    return o4 ? (n22(o4), true) : false;
  };
}
var Be4 = U6(0, false);
var Ce5 = U6(1, false);
var dt2 = U6(0, true);
var mt3 = U6(1, true);
function De5(e4) {
  return function(t5) {
    let r2 = t5.field(v3, false);
    if (!r2) return 0;
    let n22 = e4 == 0 ? r2.done : r2.undone;
    return n22.length - (n22.length && !n22[0].changes ? 1 : 0);
  };
}
var an2 = De5(0);
var hn2 = De5(1);
var g3 = class e {
  constructor(t5, r2, n22, l11, o4) {
    this.changes = t5, this.effects = r2, this.mapped = n22, this.startSelection = l11, this.selectionsAfter = o4;
  }
  setSelAfter(t5) {
    return new e(this.changes, this.effects, this.mapped, this.startSelection, t5);
  }
  toJSON() {
    var t5, r2, n22;
    return {
      changes: (t5 = this.changes) === null || t5 === void 0 ? void 0 : t5.toJSON(),
      mapped: (r2 = this.mapped) === null || r2 === void 0 ? void 0 : r2.toJSON(),
      startSelection: (n22 = this.startSelection) === null || n22 === void 0 ? void 0 : n22.toJSON(),
      selectionsAfter: this.selectionsAfter.map((l11) => l11.toJSON())
    };
  }
  static fromJSON(t5) {
    return new e(t5.changes && P.fromJSON(t5.changes), [], t5.mapped && C.fromJSON(t5.mapped), t5.startSelection && x.fromJSON(t5.startSelection), t5.selectionsAfter.map(x.fromJSON));
  }
  static fromTransaction(t5, r2) {
    let n22 = m4;
    for (let l11 of t5.startState.facet(at5)) {
      let o4 = l11(t5);
      o4.length && (n22 = n22.concat(o4));
    }
    return !n22.length && t5.changes.empty ? null : new e(t5.changes.invert(t5.startState.doc), n22, void 0, r2 || t5.startState.selection, m4);
  }
  static selection(t5) {
    return new e(void 0, m4, void 0, void 0, t5);
  }
};
function R5(e4, t5, r2, n22) {
  let l11 = t5 + 1 > r2 + 20 ? t5 - r2 - 1 : 0, o4 = e4.slice(l11, t5);
  return o4.push(n22), o4;
}
function pt3(e4, t5) {
  let r2 = [], n22 = false;
  return e4.iterChangedRanges((l11, o4) => r2.push(l11, o4)), t5.iterChangedRanges((l11, o4, c4, s99) => {
    for (let i9 = 0; i9 < r2.length; ) {
      let u5 = r2[i9++], f2 = r2[i9++];
      s99 >= u5 && c4 <= f2 && (n22 = true);
    }
  }), n22;
}
function gt2(e4, t5) {
  return e4.ranges.length == t5.ranges.length && e4.ranges.filter((r2, n22) => r2.empty != t5.ranges[n22].empty).length === 0;
}
function xe5(e4, t5) {
  return e4.length ? t5.length ? e4.concat(t5) : e4 : t5;
}
var m4 = [];
var yt3 = 200;
function Le5(e4, t5) {
  if (e4.length) {
    let r2 = e4[e4.length - 1], n22 = r2.selectionsAfter.slice(Math.max(0, r2.selectionsAfter.length - yt3));
    return n22.length && n22[n22.length - 1].eq(t5) ? e4 : (n22.push(t5), R5(e4, e4.length - 1, 1e9, r2.setSelAfter(n22)));
  } else return [
    g3.selection([
      t5
    ])
  ];
}
function kt3(e4) {
  let t5 = e4[e4.length - 1], r2 = e4.slice();
  return r2[e4.length - 1] = t5.setSelAfter(t5.selectionsAfter.slice(0, t5.selectionsAfter.length - 1)), r2;
}
function K6(e4, t5) {
  if (!e4.length) return e4;
  let r2 = e4.length, n22 = m4;
  for (; r2; ) {
    let l11 = At3(e4[r2 - 1], t5, n22);
    if (l11.changes && !l11.changes.empty || l11.effects.length) {
      let o4 = e4.slice(0, r2);
      return o4[r2 - 1] = l11, o4;
    } else t5 = l11.mapped, r2--, n22 = l11.selectionsAfter;
  }
  return n22.length ? [
    g3.selection(n22)
  ] : m4;
}
function At3(e4, t5, r2) {
  let n22 = xe5(e4.selectionsAfter.length ? e4.selectionsAfter.map((s99) => s99.map(t5)) : m4, r2);
  if (!e4.changes) return g3.selection(n22);
  let l11 = e4.changes.map(t5), o4 = t5.mapDesc(e4.changes, true), c4 = e4.mapped ? e4.mapped.composeDesc(o4) : o4;
  return new g3(l11, v.mapEffects(e4.effects, t5), c4, e4.startSelection.map(o4), n22);
}
var St3 = /^(input\.type|delete)($|\.)/;
var B6 = class e2 {
  constructor(t5, r2, n22 = 0, l11 = void 0) {
    this.done = t5, this.undone = r2, this.prevTime = n22, this.prevUserEvent = l11;
  }
  isolate() {
    return this.prevTime ? new e2(this.done, this.undone) : this;
  }
  addChanges(t5, r2, n22, l11, o4) {
    let c4 = this.done, s99 = c4[c4.length - 1];
    return s99 && s99.changes && !s99.changes.empty && t5.changes && (!n22 || St3.test(n22)) && (!s99.selectionsAfter.length && r2 - this.prevTime < l11 && pt3(s99.changes, t5.changes) || n22 == "input.type.compose") ? c4 = R5(c4, c4.length - 1, o4, new g3(t5.changes.compose(s99.changes), xe5(t5.effects, s99.effects), s99.mapped, s99.startSelection, m4)) : c4 = R5(c4, c4.length, o4, t5), new e2(c4, m4, r2, n22);
  }
  addSelection(t5, r2, n22, l11) {
    let o4 = this.done.length ? this.done[this.done.length - 1].selectionsAfter : m4;
    return o4.length > 0 && r2 - this.prevTime < l11 && n22 == this.prevUserEvent && n22 && /^select($|\.)/.test(n22) && gt2(o4[o4.length - 1], t5) ? this : new e2(Le5(this.done, t5), this.undone, r2, n22);
  }
  addMapping(t5) {
    return new e2(K6(this.done, t5), K6(this.undone, t5), this.prevTime, this.prevUserEvent);
  }
  pop(t5, r2, n22) {
    let l11 = t5 == 0 ? this.done : this.undone;
    if (l11.length == 0) return null;
    let o4 = l11[l11.length - 1];
    if (n22 && o4.selectionsAfter.length) return r2.update({
      selection: o4.selectionsAfter[o4.selectionsAfter.length - 1],
      annotations: X7.of({
        side: t5,
        rest: kt3(l11)
      }),
      userEvent: t5 == 0 ? "select.undo" : "select.redo",
      scrollIntoView: true
    });
    if (o4.changes) {
      let c4 = l11.length == 1 ? m4 : l11.slice(0, l11.length - 1);
      return o4.mapped && (c4 = K6(c4, o4.mapped)), r2.update({
        changes: o4.changes,
        selection: o4.startSelection,
        effects: o4.effects,
        annotations: X7.of({
          side: t5,
          rest: c4
        }),
        filter: false,
        userEvent: t5 == 0 ? "undo" : "redo",
        scrollIntoView: true
      });
    } else return null;
  }
};
B6.empty = new B6(m4, m4);
var dn = [
  {
    key: "Mod-z",
    run: Be4,
    preventDefault: true
  },
  {
    key: "Mod-y",
    mac: "Mod-Shift-z",
    run: Ce5,
    preventDefault: true
  },
  {
    key: "Mod-u",
    run: dt2,
    preventDefault: true
  },
  {
    key: "Alt-u",
    mac: "Mod-Shift-u",
    run: mt3,
    preventDefault: true
  }
];
function x5(e4, t5) {
  return x.create(e4.ranges.map(t5), e4.mainIndex);
}
function k4(e4, t5) {
  return e4.update({
    selection: t5,
    scrollIntoView: true,
    userEvent: "select"
  });
}
function A6({ state: e4, dispatch: t5 }, r2) {
  let n22 = x5(e4.selection, r2);
  return n22.eq(e4.selection) ? false : (t5(k4(e4, n22)), true);
}
function E4(e4, t5) {
  return x.cursor(t5 ? e4.to : e4.from);
}
function N6(e4, t5) {
  return A6(e4, (r2) => r2.empty ? e4.moveByChar(r2, t5) : E4(r2, t5));
}
function p2(e4) {
  return e4.textDirectionAt(e4.state.selection.main.head) == O2.LTR;
}
var Me4 = (e4) => N6(e4, !p2(e4));
var Ee3 = (e4) => N6(e4, p2(e4));
function G3(e4, t5) {
  return A6(e4, (r2) => r2.empty ? e4.moveByGroup(r2, t5) : E4(r2, t5));
}
var Bt4 = (e4) => G3(e4, !p2(e4));
var Ct4 = (e4) => G3(e4, p2(e4));
function Dt4(e4, t5, r2) {
  if (t5.type.prop(r2)) return true;
  let n22 = t5.to - t5.from;
  return n22 && (n22 > 2 || /[^\s,.;:]/.test(e4.sliceDoc(t5.from, t5.to))) || t5.firstChild;
}
function V7(e4, t5, r2) {
  let n22 = m3(e4).resolveInner(t5.head), l11 = r2 ? w3.closedBy : w3.openedBy;
  for (let i9 = t5.head; ; ) {
    let u5 = r2 ? n22.childAfter(i9) : n22.childBefore(i9);
    if (!u5) break;
    Dt4(e4, u5, l11) ? n22 = u5 : i9 = r2 ? u5.to : u5.from;
  }
  let o4 = n22.type.prop(l11), c4, s99;
  return o4 && (c4 = r2 ? M4(e4, n22.from, 1) : M4(e4, n22.to, -1)) && c4.matched ? s99 = r2 ? c4.end.to : c4.end.from : s99 = r2 ? n22.to : n22.from, x.cursor(s99, r2 ? -1 : 1);
}
var xt4 = (e4) => A6(e4, (t5) => V7(e4.state, t5, !p2(e4)));
var Lt4 = (e4) => A6(e4, (t5) => V7(e4.state, t5, p2(e4)));
function Te5(e4, t5) {
  return A6(e4, (r2) => {
    if (!r2.empty) return E4(r2, t5);
    let n22 = e4.moveVertically(r2, t5);
    return n22.head != r2.head ? n22 : e4.moveToLineBoundary(r2, t5);
  });
}
var Ie4 = (e4) => Te5(e4, false);
var Re4 = (e4) => Te5(e4, true);
function we4(e4, t5) {
  let { state: r2 } = e4, n22 = x5(r2.selection, (s99) => s99.empty ? e4.moveVertically(s99, t5, Math.min(e4.dom.clientHeight, innerHeight)) : E4(s99, t5));
  if (n22.eq(r2.selection)) return false;
  let l11 = e4.coordsAtPos(r2.selection.main.head), o4 = e4.scrollDOM.getBoundingClientRect(), c4;
  return l11 && l11.top > o4.top && l11.bottom < o4.bottom && l11.top - o4.top <= e4.scrollDOM.scrollHeight - e4.scrollDOM.scrollTop - e4.scrollDOM.clientHeight && (c4 = M2.scrollIntoView(n22.main.head, {
    y: "start",
    yMargin: l11.top - o4.top
  })), e4.dispatch(k4(r2, n22), {
    effects: c4
  }), true;
}
var re5 = (e4) => we4(e4, false);
var Y5 = (e4) => we4(e4, true);
function P4(e4, t5, r2) {
  let n22 = e4.lineBlockAt(t5.head), l11 = e4.moveToLineBoundary(t5, r2);
  if (l11.head == t5.head && l11.head != (r2 ? n22.to : n22.from) && (l11 = e4.moveToLineBoundary(t5, r2, false)), !r2 && l11.head == n22.from && n22.length) {
    let o4 = /^\s*/.exec(e4.state.sliceDoc(n22.from, Math.min(n22.from + 100, n22.to)))[0].length;
    o4 && t5.head != n22.from + o4 && (l11 = x.cursor(n22.from + o4));
  }
  return l11;
}
var oe5 = (e4) => A6(e4, (t5) => P4(e4, t5, true));
var le4 = (e4) => A6(e4, (t5) => P4(e4, t5, false));
var Mt4 = (e4) => A6(e4, (t5) => x.cursor(e4.lineBlockAt(t5.head).from, 1));
var Et3 = (e4) => A6(e4, (t5) => x.cursor(e4.lineBlockAt(t5.head).to, -1));
function ve4(e4, t5, r2) {
  let n22 = false, l11 = x5(e4.selection, (o4) => {
    let c4 = M4(e4, o4.head, -1) || M4(e4, o4.head, 1) || o4.head > 0 && M4(e4, o4.head - 1, 1) || o4.head < e4.doc.length && M4(e4, o4.head + 1, -1);
    if (!c4 || !c4.end) return o4;
    n22 = true;
    let s99 = c4.start.from == o4.head ? c4.end.to : c4.end.from;
    return r2 ? x.range(o4.anchor, s99) : x.cursor(s99);
  });
  return n22 ? (t5(k4(e4, l11)), true) : false;
}
var Ot4 = ({ state: e4, dispatch: t5 }) => ve4(e4, t5, false);
function y4(e4, t5) {
  let r2 = x5(e4.state.selection, (n22) => {
    let l11 = t5(n22);
    return x.range(n22.anchor, l11.head, l11.goalColumn);
  });
  return r2.eq(e4.state.selection) ? false : (e4.dispatch(k4(e4.state, r2)), true);
}
function J4(e4, t5) {
  return y4(e4, (r2) => e4.moveByChar(r2, t5));
}
var Ue4 = (e4) => J4(e4, !p2(e4));
var Ne3 = (e4) => J4(e4, p2(e4));
function F5(e4, t5) {
  return y4(e4, (r2) => e4.moveByGroup(r2, t5));
}
var bt3 = (e4) => F5(e4, !p2(e4));
var Tt4 = (e4) => F5(e4, p2(e4));
var It4 = (e4) => y4(e4, (t5) => V7(e4.state, t5, !p2(e4)));
var Rt3 = (e4) => y4(e4, (t5) => V7(e4.state, t5, p2(e4)));
function Ve3(e4, t5) {
  return y4(e4, (r2) => e4.moveVertically(r2, t5));
}
var Pe5 = (e4) => Ve3(e4, false);
var Je4 = (e4) => Ve3(e4, true);
function Fe4(e4, t5) {
  return y4(e4, (r2) => e4.moveVertically(r2, t5, Math.min(e4.dom.clientHeight, innerHeight)));
}
var ce6 = (e4) => Fe4(e4, false);
var se6 = (e4) => Fe4(e4, true);
var ie5 = (e4) => y4(e4, (t5) => P4(e4, t5, true));
var ue6 = (e4) => y4(e4, (t5) => P4(e4, t5, false));
var wt3 = (e4) => y4(e4, (t5) => x.cursor(e4.lineBlockAt(t5.head).from));
var vt3 = (e4) => y4(e4, (t5) => x.cursor(e4.lineBlockAt(t5.head).to));
var fe4 = ({ state: e4, dispatch: t5 }) => (t5(k4(e4, {
  anchor: 0
})), true);
var ae5 = ({ state: e4, dispatch: t5 }) => (t5(k4(e4, {
  anchor: e4.doc.length
})), true);
var he6 = ({ state: e4, dispatch: t5 }) => (t5(k4(e4, {
  anchor: e4.selection.main.anchor,
  head: 0
})), true);
var de5 = ({ state: e4, dispatch: t5 }) => (t5(k4(e4, {
  anchor: e4.selection.main.anchor,
  head: e4.doc.length
})), true);
var Ut3 = ({ state: e4, dispatch: t5 }) => (t5(e4.update({
  selection: {
    anchor: 0,
    head: e4.doc.length
  },
  userEvent: "select"
})), true);
var Nt3 = ({ state: e4, dispatch: t5 }) => {
  let r2 = q4(e4).map(({ from: n22, to: l11 }) => x.range(n22, Math.min(l11 + 1, e4.doc.length)));
  return t5(e4.update({
    selection: x.create(r2),
    userEvent: "select"
  })), true;
};
var Gt2 = ({ state: e4, dispatch: t5 }) => {
  let r2 = x5(e4.selection, (n22) => {
    var l11;
    let o4 = m3(e4).resolveInner(n22.head, 1);
    for (; !(o4.from < n22.from && o4.to >= n22.to || o4.to > n22.to && o4.from <= n22.from || !(!((l11 = o4.parent) === null || l11 === void 0) && l11.parent)); ) o4 = o4.parent;
    return x.range(o4.to, o4.from);
  });
  return t5(k4(e4, r2)), true;
};
var Vt = ({ state: e4, dispatch: t5 }) => {
  let r2 = e4.selection, n22 = null;
  return r2.ranges.length > 1 ? n22 = x.create([
    r2.main
  ]) : r2.main.empty || (n22 = x.create([
    x.cursor(r2.main.head)
  ])), n22 ? (t5(k4(e4, n22)), true) : false;
};
function H4({ state: e4, dispatch: t5 }, r2) {
  if (e4.readOnly) return false;
  let n22 = "delete.selection", l11 = e4.changeByRange((o4) => {
    let { from: c4, to: s99 } = o4;
    if (c4 == s99) {
      let i9 = r2(c4);
      i9 < c4 ? n22 = "delete.backward" : i9 > c4 && (n22 = "delete.forward"), c4 = Math.min(c4, i9), s99 = Math.max(s99, i9);
    }
    return c4 == s99 ? {
      range: o4
    } : {
      changes: {
        from: c4,
        to: s99
      },
      range: x.cursor(c4)
    };
  });
  return l11.changes.empty ? false : (t5(e4.update(l11, {
    scrollIntoView: true,
    userEvent: n22
  })), true);
}
function z5(e4, t5, r2) {
  if (e4 instanceof M2) for (let n22 of e4.state.facet(M2.atomicRanges).map((l11) => l11(e4))) n22.between(t5, t5, (l11, o4) => {
    l11 < t5 && o4 > t5 && (t5 = r2 ? o4 : l11);
  });
  return t5;
}
var He3 = (e4, t5) => H4(e4, (r2) => {
  let { state: n22 } = e4, l11 = n22.doc.lineAt(r2), o4, c4;
  if (!t5 && r2 > l11.from && r2 < l11.from + 200 && !/[^ \t]/.test(o4 = l11.text.slice(0, r2 - l11.from))) {
    if (o4[o4.length - 1] == "	") return r2 - 1;
    let s99 = ot(o4, n22.tabSize), i9 = s99 % L3(n22) || L3(n22);
    for (let u5 = 0; u5 < i9 && o4[o4.length - 1 - u5] == " "; u5++) r2--;
    c4 = r2;
  } else c4 = _(l11.text, r2 - l11.from, t5, t5) + l11.from, c4 == r2 && l11.number != (t5 ? n22.doc.lines : 1) && (c4 += t5 ? 1 : -1);
  return z5(e4, c4, t5);
});
var Z7 = (e4) => He3(e4, false);
var ze3 = (e4) => He3(e4, true);
var qe3 = (e4, t5) => H4(e4, (r2) => {
  let n22 = r2, { state: l11 } = e4, o4 = l11.doc.lineAt(n22), c4 = l11.charCategorizer(n22);
  for (let s99 = null; ; ) {
    if (n22 == (t5 ? o4.to : o4.from)) {
      n22 == r2 && o4.number != (t5 ? l11.doc.lines : 1) && (n22 += t5 ? 1 : -1);
      break;
    }
    let i9 = _(o4.text, n22 - o4.from, t5) + o4.from, u5 = o4.text.slice(Math.min(n22, i9) - o4.from, Math.max(n22, i9) - o4.from), f2 = c4(u5);
    if (s99 != null && f2 != s99) break;
    (u5 != " " || n22 != r2) && (s99 = f2), n22 = i9;
  }
  return z5(e4, n22, t5);
});
var $e3 = (e4) => qe3(e4, false);
var Pt4 = (e4) => qe3(e4, true);
var Ke3 = (e4) => H4(e4, (t5) => {
  let r2 = e4.lineBlockAt(t5).to;
  return z5(e4, t5 < r2 ? r2 : Math.min(e4.state.doc.length, t5 + 1), true);
});
var Jt2 = (e4) => H4(e4, (t5) => {
  let r2 = e4.lineBlockAt(t5).from;
  return z5(e4, t5 > r2 ? r2 : Math.max(0, t5 - 1), false);
});
var Ft2 = ({ state: e4, dispatch: t5 }) => {
  if (e4.readOnly) return false;
  let r2 = e4.changeByRange((n22) => ({
    changes: {
      from: n22.from,
      to: n22.to,
      insert: m.of([
        "",
        ""
      ])
    },
    range: x.cursor(n22.from)
  }));
  return t5(e4.update(r2, {
    scrollIntoView: true,
    userEvent: "input"
  })), true;
};
var Ht3 = ({ state: e4, dispatch: t5 }) => {
  if (e4.readOnly) return false;
  let r2 = e4.changeByRange((n22) => {
    if (!n22.empty || n22.from == 0 || n22.from == e4.doc.length) return {
      range: n22
    };
    let l11 = n22.from, o4 = e4.doc.lineAt(l11), c4 = l11 == o4.from ? l11 - 1 : _(o4.text, l11 - o4.from, false) + o4.from, s99 = l11 == o4.to ? l11 + 1 : _(o4.text, l11 - o4.from, true) + o4.from;
    return {
      changes: {
        from: c4,
        to: s99,
        insert: e4.doc.slice(l11, s99).append(e4.doc.slice(c4, l11))
      },
      range: x.cursor(s99)
    };
  });
  return r2.changes.empty ? false : (t5(e4.update(r2, {
    scrollIntoView: true,
    userEvent: "move.character"
  })), true);
};
function q4(e4) {
  let t5 = [], r2 = -1;
  for (let n22 of e4.selection.ranges) {
    let l11 = e4.doc.lineAt(n22.from), o4 = e4.doc.lineAt(n22.to);
    if (!n22.empty && n22.to == o4.from && (o4 = e4.doc.lineAt(n22.to - 1)), r2 >= l11.number) {
      let c4 = t5[t5.length - 1];
      c4.to = o4.to, c4.ranges.push(n22);
    } else t5.push({
      from: l11.from,
      to: o4.to,
      ranges: [
        n22
      ]
    });
    r2 = o4.number + 1;
  }
  return t5;
}
function We3(e4, t5, r2) {
  if (e4.readOnly) return false;
  let n22 = [], l11 = [];
  for (let o4 of q4(e4)) {
    if (r2 ? o4.to == e4.doc.length : o4.from == 0) continue;
    let c4 = e4.doc.lineAt(r2 ? o4.to + 1 : o4.from - 1), s99 = c4.length + 1;
    if (r2) {
      n22.push({
        from: o4.to,
        to: c4.to
      }, {
        from: o4.from,
        insert: c4.text + e4.lineBreak
      });
      for (let i9 of o4.ranges) l11.push(x.range(Math.min(e4.doc.length, i9.anchor + s99), Math.min(e4.doc.length, i9.head + s99)));
    } else {
      n22.push({
        from: c4.from,
        to: o4.from
      }, {
        from: o4.to,
        insert: e4.lineBreak + c4.text
      });
      for (let i9 of o4.ranges) l11.push(x.range(i9.anchor - s99, i9.head - s99));
    }
  }
  return n22.length ? (t5(e4.update({
    changes: n22,
    scrollIntoView: true,
    selection: x.create(l11, e4.selection.mainIndex),
    userEvent: "move.line"
  })), true) : false;
}
var zt2 = ({ state: e4, dispatch: t5 }) => We3(e4, t5, false);
var qt2 = ({ state: e4, dispatch: t5 }) => We3(e4, t5, true);
function Qe3(e4, t5, r2) {
  if (e4.readOnly) return false;
  let n22 = [];
  for (let l11 of q4(e4)) r2 ? n22.push({
    from: l11.from,
    insert: e4.doc.slice(l11.from, l11.to) + e4.lineBreak
  }) : n22.push({
    from: l11.to,
    insert: e4.lineBreak + e4.doc.slice(l11.from, l11.to)
  });
  return t5(e4.update({
    changes: n22,
    scrollIntoView: true,
    userEvent: "input.copyline"
  })), true;
}
var $t2 = ({ state: e4, dispatch: t5 }) => Qe3(e4, t5, false);
var Kt2 = ({ state: e4, dispatch: t5 }) => Qe3(e4, t5, true);
var Wt2 = (e4) => {
  if (e4.state.readOnly) return false;
  let { state: t5 } = e4, r2 = t5.changes(q4(t5).map(({ from: l11, to: o4 }) => (l11 > 0 ? l11-- : o4 < t5.doc.length && o4++, {
    from: l11,
    to: o4
  }))), n22 = x5(t5.selection, (l11) => e4.moveVertically(l11, true)).map(r2);
  return e4.dispatch({
    changes: r2,
    selection: n22,
    scrollIntoView: true,
    userEvent: "delete.line"
  }), true;
};
function Qt3(e4, t5) {
  if (/\(\)|\[\]|\{\}/.test(e4.sliceDoc(t5 - 1, t5 + 1))) return {
    from: t5,
    to: t5
  };
  let r2 = m3(e4).resolveInner(t5), n22 = r2.childBefore(t5), l11 = r2.childAfter(t5), o4;
  return n22 && l11 && n22.to <= t5 && l11.from >= t5 && (o4 = n22.type.prop(w3.closedBy)) && o4.indexOf(l11.name) > -1 && e4.doc.lineAt(n22.to).from == e4.doc.lineAt(l11.from).from ? {
    from: n22.to,
    to: l11.from
  } : null;
}
var Xt3 = Xe4(false);
var Yt2 = Xe4(true);
function Xe4(e4) {
  return ({ state: t5, dispatch: r2 }) => {
    if (t5.readOnly) return false;
    let n22 = t5.changeByRange((l11) => {
      let { from: o4, to: c4 } = l11, s99 = t5.doc.lineAt(o4), i9 = !e4 && o4 == c4 && Qt3(t5, o4);
      e4 && (o4 = c4 = (c4 <= s99.to ? s99 : t5.doc.lineAt(c4)).to);
      let u5 = new R4(t5, {
        simulateBreak: o4,
        simulateDoubleBreak: !!i9
      }), f2 = ee3(u5, o4);
      for (f2 == null && (f2 = /^\s*/.exec(t5.doc.lineAt(o4).text)[0].length); c4 < s99.to && /\s/.test(s99.text[c4 - s99.from]); ) c4++;
      i9 ? { from: o4, to: c4 } = i9 : o4 > s99.from && o4 < s99.from + 100 && !/\S/.test(s99.text.slice(0, o4)) && (o4 = s99.from);
      let a2 = [
        "",
        te3(t5, f2)
      ];
      return i9 && a2.push(te3(t5, u5.lineIndent(s99.from, -1))), {
        changes: {
          from: o4,
          to: c4,
          insert: m.of(a2)
        },
        range: x.cursor(o4 + 1 + a2[1].length)
      };
    });
    return r2(t5.update(n22, {
      scrollIntoView: true,
      userEvent: "input"
    })), true;
  };
}
function te4(e4, t5) {
  let r2 = -1;
  return e4.changeByRange((n22) => {
    let l11 = [];
    for (let c4 = n22.from; c4 <= n22.to; ) {
      let s99 = e4.doc.lineAt(c4);
      s99.number > r2 && (n22.empty || n22.to > s99.from) && (t5(s99, l11, n22), r2 = s99.number), c4 = s99.to + 1;
    }
    let o4 = e4.changes(l11);
    return {
      changes: l11,
      range: x.range(o4.mapPos(n22.anchor, 1), o4.mapPos(n22.head, 1))
    };
  });
}
var Zt2 = ({ state: e4, dispatch: t5 }) => {
  if (e4.readOnly) return false;
  let r2 = /* @__PURE__ */ Object.create(null), n22 = new R4(e4, {
    overrideIndentation: (o4) => {
      let c4 = r2[o4];
      return c4 ?? -1;
    }
  }), l11 = te4(e4, (o4, c4, s99) => {
    let i9 = ee3(n22, o4.from);
    if (i9 == null) return;
    /\S/.test(o4.text) || (i9 = 0);
    let u5 = /^\s*/.exec(o4.text)[0], f2 = te3(e4, i9);
    (u5 != f2 || s99.from < o4.from + u5.length) && (r2[o4.from] = i9, c4.push({
      from: o4.from,
      to: o4.from + u5.length,
      insert: f2
    }));
  });
  return l11.changes.empty || t5(e4.update(l11, {
    userEvent: "indent"
  })), true;
};
var ne5 = ({ state: e4, dispatch: t5 }) => e4.readOnly ? false : (t5(e4.update(te4(e4, (r2, n22) => {
  n22.push({
    from: r2.from,
    insert: e4.facet(Pt2)
  });
}), {
  userEvent: "input.indent"
})), true);
var Ye4 = ({ state: e4, dispatch: t5 }) => e4.readOnly ? false : (t5(e4.update(te4(e4, (r2, n22) => {
  let l11 = /^\s*/.exec(r2.text)[0];
  if (!l11) return;
  let o4 = ot(l11, e4.tabSize), c4 = 0, s99 = te3(e4, Math.max(0, o4 - L3(e4)));
  for (; c4 < l11.length && c4 < s99.length && l11.charCodeAt(c4) == s99.charCodeAt(c4); ) c4++;
  n22.push({
    from: r2.from + c4,
    to: r2.from + l11.length,
    insert: s99.slice(c4)
  });
}), {
  userEvent: "delete.dedent"
})), true);
var _t2 = [
  {
    key: "Ctrl-b",
    run: Me4,
    shift: Ue4,
    preventDefault: true
  },
  {
    key: "Ctrl-f",
    run: Ee3,
    shift: Ne3
  },
  {
    key: "Ctrl-p",
    run: Ie4,
    shift: Pe5
  },
  {
    key: "Ctrl-n",
    run: Re4,
    shift: Je4
  },
  {
    key: "Ctrl-a",
    run: Mt4,
    shift: wt3
  },
  {
    key: "Ctrl-e",
    run: Et3,
    shift: vt3
  },
  {
    key: "Ctrl-d",
    run: ze3
  },
  {
    key: "Ctrl-h",
    run: Z7
  },
  {
    key: "Ctrl-k",
    run: Ke3
  },
  {
    key: "Ctrl-Alt-h",
    run: $e3
  },
  {
    key: "Ctrl-o",
    run: Ft2
  },
  {
    key: "Ctrl-t",
    run: Ht3
  },
  {
    key: "Ctrl-v",
    run: Y5
  }
];
var jt4 = [
  {
    key: "ArrowLeft",
    run: Me4,
    shift: Ue4,
    preventDefault: true
  },
  {
    key: "Mod-ArrowLeft",
    mac: "Alt-ArrowLeft",
    run: Bt4,
    shift: bt3
  },
  {
    mac: "Cmd-ArrowLeft",
    run: le4,
    shift: ue6
  },
  {
    key: "ArrowRight",
    run: Ee3,
    shift: Ne3,
    preventDefault: true
  },
  {
    key: "Mod-ArrowRight",
    mac: "Alt-ArrowRight",
    run: Ct4,
    shift: Tt4
  },
  {
    mac: "Cmd-ArrowRight",
    run: oe5,
    shift: ie5
  },
  {
    key: "ArrowUp",
    run: Ie4,
    shift: Pe5,
    preventDefault: true
  },
  {
    mac: "Cmd-ArrowUp",
    run: fe4,
    shift: he6
  },
  {
    mac: "Ctrl-ArrowUp",
    run: re5,
    shift: ce6
  },
  {
    key: "ArrowDown",
    run: Re4,
    shift: Je4,
    preventDefault: true
  },
  {
    mac: "Cmd-ArrowDown",
    run: ae5,
    shift: de5
  },
  {
    mac: "Ctrl-ArrowDown",
    run: Y5,
    shift: se6
  },
  {
    key: "PageUp",
    run: re5,
    shift: ce6
  },
  {
    key: "PageDown",
    run: Y5,
    shift: se6
  },
  {
    key: "Home",
    run: le4,
    shift: ue6,
    preventDefault: true
  },
  {
    key: "Mod-Home",
    run: fe4,
    shift: he6
  },
  {
    key: "End",
    run: oe5,
    shift: ie5,
    preventDefault: true
  },
  {
    key: "Mod-End",
    run: ae5,
    shift: de5
  },
  {
    key: "Enter",
    run: Xt3
  },
  {
    key: "Mod-a",
    run: Ut3
  },
  {
    key: "Backspace",
    run: Z7,
    shift: Z7
  },
  {
    key: "Delete",
    run: ze3
  },
  {
    key: "Mod-Backspace",
    mac: "Alt-Backspace",
    run: $e3
  },
  {
    key: "Mod-Delete",
    mac: "Alt-Delete",
    run: Pt4
  },
  {
    mac: "Mod-Backspace",
    run: Jt2
  },
  {
    mac: "Mod-Delete",
    run: Ke3
  }
].concat(_t2.map((e4) => ({
  mac: e4.key,
  run: e4.run,
  shift: e4.shift
})));
var Tn2 = [
  {
    key: "Alt-ArrowLeft",
    mac: "Ctrl-ArrowLeft",
    run: xt4,
    shift: It4
  },
  {
    key: "Alt-ArrowRight",
    mac: "Ctrl-ArrowRight",
    run: Lt4,
    shift: Rt3
  },
  {
    key: "Alt-ArrowUp",
    run: zt2
  },
  {
    key: "Shift-Alt-ArrowUp",
    run: $t2
  },
  {
    key: "Alt-ArrowDown",
    run: qt2
  },
  {
    key: "Shift-Alt-ArrowDown",
    run: Kt2
  },
  {
    key: "Escape",
    run: Vt
  },
  {
    key: "Mod-Enter",
    run: Yt2
  },
  {
    key: "Alt-l",
    mac: "Ctrl-l",
    run: Nt3
  },
  {
    key: "Mod-i",
    run: Gt2,
    preventDefault: true
  },
  {
    key: "Mod-[",
    run: Ye4
  },
  {
    key: "Mod-]",
    run: ne5
  },
  {
    key: "Mod-Alt-\\",
    run: Zt2
  },
  {
    key: "Shift-Mod-k",
    run: Wt2
  },
  {
    key: "Shift-Mod-\\",
    run: Ot4
  },
  {
    key: "Mod-/",
    run: ot5
  },
  {
    key: "Alt-A",
    run: ct3
  }
].concat(jt4);

// deno:https://esm.sh/crelt@1.0.6/denonext/crelt.mjs
function s45() {
  var r2 = arguments[0];
  typeof r2 == "string" && (r2 = document.createElement(r2));
  var e4 = 1, t5 = arguments[1];
  if (t5 && typeof t5 == "object" && t5.nodeType == null && !Array.isArray(t5)) {
    for (var n22 in t5) if (Object.prototype.hasOwnProperty.call(t5, n22)) {
      var o4 = t5[n22];
      typeof o4 == "string" ? r2.setAttribute(n22, o4) : o4 != null && (r2[n22] = o4);
    }
    e4++;
  }
  for (; e4 < arguments.length; e4++) f(r2, arguments[e4]);
  return r2;
}
function f(r2, e4) {
  if (typeof e4 == "string") r2.appendChild(document.createTextNode(e4));
  else if (e4 != null) if (e4.nodeType != null) r2.appendChild(e4);
  else if (Array.isArray(e4)) for (var t5 = 0; t5 < e4.length; t5++) f(r2, e4[t5]);
  else throw new RangeError("Unsupported child node: " + e4);
}

// deno:https://esm.sh/@codemirror/lint@0.20.3/denonext/lint.mjs
var R6 = class {
  constructor(e4, o4, i9) {
    this.from = e4, this.to = o4, this.diagnostic = i9;
  }
};
var m5 = class t3 {
  constructor(e4, o4, i9) {
    this.diagnostics = e4, this.panel = o4, this.selected = i9;
  }
  static init(e4, o4, i9) {
    let n22 = e4, s99 = i9.facet(h).markerFilter;
    s99 && (n22 = s99(n22));
    let r2 = C2.set(n22.map((l11) => l11.from == l11.to || l11.from == l11.to - 1 && i9.doc.lineAt(l11.from).to == l11.from ? C2.widget({
      widget: new L5(l11),
      diagnostic: l11
    }).range(l11.from) : C2.mark({
      attributes: {
        class: "cm-lintRange cm-lintRange-" + l11.severity
      },
      diagnostic: l11
    }).range(l11.from, l11.to)), true);
    return new t3(r2, o4, b4(r2));
  }
};
function b4(t5, e4 = null, o4 = 0) {
  let i9 = null;
  return t5.between(o4, 1e9, (n22, s99, { spec: r2 }) => {
    if (!(e4 && r2.diagnostic != e4)) return i9 = new R6(n22, s99, r2.diagnostic), false;
  }), i9;
}
function j5(t5, e4) {
  return !!(t5.effects.some((o4) => o4.is(C7)) || t5.changes.touchesRange(e4.pos));
}
function G4(t5, e4) {
  return t5.field(d, false) ? e4 : e4.concat(v.appendConfig.of([
    d,
    M2.decorations.compute([
      d
    ], (o4) => {
      let { selected: i9, panel: n22 } = o4.field(d);
      return !i9 || !n22 || i9.from == i9.to ? C2.none : C2.set([
        ie6.range(i9.from, i9.to)
      ]);
    }),
    lo(oe6, {
      hideOn: j5
    }),
    le5
  ]));
}
function te5(t5, e4) {
  return {
    effects: G4(t5, [
      C7.of(e4)
    ])
  };
}
var C7 = v.define();
var F6 = v.define();
var $4 = v.define();
var d = $.define({
  create() {
    return new m5(C2.none, null, null);
  },
  update(t5, e4) {
    if (e4.docChanged) {
      let o4 = t5.diagnostics.map(e4.changes), i9 = null;
      if (t5.selected) {
        let n22 = e4.changes.mapPos(t5.selected.from, 1);
        i9 = b4(o4, t5.selected.diagnostic, n22) || b4(o4, null, n22);
      }
      t5 = new m5(o4, t5.panel, i9);
    }
    for (let o4 of e4.effects) o4.is(C7) ? t5 = m5.init(o4.value, t5.panel, e4.state) : o4.is(F6) ? t5 = new m5(t5.diagnostics, o4.value ? y5.open : null, t5.selected) : o4.is($4) && (t5 = new m5(t5.diagnostics, t5.panel, o4.value));
    return t5;
  },
  provide: (t5) => [
    ns.from(t5, (e4) => e4.panel),
    M2.decorations.from(t5, (e4) => e4.diagnostics)
  ]
});
var ie6 = C2.mark({
  class: "cm-lintRange cm-lintRange-active"
});
function oe6(t5, e4, o4) {
  let { diagnostics: i9 } = t5.state.field(d), n22 = [], s99 = 2e8, r2 = 0;
  i9.between(e4 - (o4 < 0 ? 1 : 0), e4 + (o4 > 0 ? 1 : 0), (a2, c4, { spec: f2 }) => {
    e4 >= a2 && e4 <= c4 && (a2 == c4 || (e4 > a2 || o4 > 0) && (e4 < c4 || o4 < 0)) && (n22.push(f2.diagnostic), s99 = Math.min(a2, s99), r2 = Math.max(c4, r2));
  });
  let l11 = t5.state.facet(h).tooltipFilter;
  return l11 && (n22 = l11(n22)), n22.length ? {
    pos: s99,
    end: r2,
    above: t5.state.doc.lineAt(s99).to < r2,
    create() {
      return {
        dom: H5(t5, n22)
      };
    }
  } : null;
}
function H5(t5, e4) {
  return s45("ul", {
    class: "cm-tooltip-lint"
  }, e4.map((o4) => _5(t5, o4, false)));
}
var ne6 = (t5) => {
  let e4 = t5.state.field(d, false);
  (!e4 || !e4.panel) && t5.dispatch({
    effects: G4(t5.state, [
      F6.of(true)
    ])
  });
  let o4 = po(t5, y5.open);
  return o4 && o4.dom.querySelector(".cm-panel-lint ul").focus(), true;
};
var I5 = (t5) => {
  let e4 = t5.state.field(d, false);
  return !e4 || !e4.panel ? false : (t5.dispatch({
    effects: F6.of(false)
  }), true);
};
var se7 = (t5) => {
  let e4 = t5.state.field(d, false);
  if (!e4) return false;
  let o4 = t5.state.selection.main, i9 = e4.diagnostics.iter(o4.to + 1);
  return !i9.value && (i9 = e4.diagnostics.iter(0), !i9.value || i9.from == o4.from && i9.to == o4.to) ? false : (t5.dispatch({
    selection: {
      anchor: i9.from,
      head: i9.to
    },
    scrollIntoView: true
  }), true);
};
var pe5 = [
  {
    key: "Mod-Shift-m",
    run: ne6
  },
  {
    key: "F8",
    run: se7
  }
];
var N7 = P2.fromClass(class {
  constructor(t5) {
    this.view = t5, this.timeout = -1, this.set = true;
    let { delay: e4 } = t5.state.facet(h);
    this.lintTime = Date.now() + e4, this.run = this.run.bind(this), this.timeout = setTimeout(this.run, e4);
  }
  run() {
    let t5 = Date.now();
    if (t5 < this.lintTime - 10) setTimeout(this.run, this.lintTime - t5);
    else {
      this.set = false;
      let { state: e4 } = this.view, { sources: o4 } = e4.facet(h);
      Promise.all(o4.map((i9) => Promise.resolve(i9(this.view)))).then((i9) => {
        let n22 = i9.reduce((s99, r2) => s99.concat(r2));
        this.view.state.doc == e4.doc && this.view.dispatch(te5(this.view.state, n22));
      }, (i9) => {
        Z2(this.view.state, i9);
      });
    }
  }
  update(t5) {
    let e4 = t5.state.facet(h);
    (t5.docChanged || e4 != t5.startState.facet(h)) && (this.lintTime = Date.now() + e4.delay, this.set || (this.set = true, this.timeout = setTimeout(this.run, e4.delay)));
  }
  force() {
    this.set && (this.lintTime = Date.now(), this.run());
  }
  destroy() {
    clearTimeout(this.timeout);
  }
});
var h = y.define({
  combine(t5) {
    return Object.assign({
      sources: t5.map((e4) => e4.source)
    }, ht(t5.map((e4) => e4.config), {
      delay: 750,
      markerFilter: null,
      tooltipFilter: null
    }));
  },
  enables: N7
});
function V8(t5) {
  let e4 = [];
  if (t5) e: for (let { name: o4 } of t5) {
    for (let i9 = 0; i9 < o4.length; i9++) {
      let n22 = o4[i9];
      if (/[a-zA-Z]/.test(n22) && !e4.some((s99) => s99.toLowerCase() == n22.toLowerCase())) {
        e4.push(n22);
        continue e;
      }
    }
    e4.push("");
  }
  return e4;
}
function _5(t5, e4, o4) {
  var i9;
  let n22 = o4 ? V8(e4.actions) : [];
  return s45("li", {
    class: "cm-diagnostic cm-diagnostic-" + e4.severity
  }, s45("span", {
    class: "cm-diagnosticText"
  }, e4.renderMessage ? e4.renderMessage() : e4.message), (i9 = e4.actions) === null || i9 === void 0 ? void 0 : i9.map((s99, r2) => {
    let l11 = (p5) => {
      p5.preventDefault();
      let S11 = b4(t5.state.field(d).diagnostics, e4);
      S11 && s99.apply(t5, S11.from, S11.to);
    }, { name: a2 } = s99, c4 = n22[r2] ? a2.indexOf(n22[r2]) : -1, f2 = c4 < 0 ? a2 : [
      a2.slice(0, c4),
      s45("u", a2.slice(c4, c4 + 1)),
      a2.slice(c4 + 1)
    ];
    return s45("button", {
      type: "button",
      class: "cm-diagnosticAction",
      onclick: l11,
      onmousedown: l11,
      "aria-label": ` Action: ${a2}${c4 < 0 ? "" : ` (access key "${n22[r2]})"`}.`
    }, f2);
  }), e4.source && s45("div", {
    class: "cm-diagnosticSource"
  }, e4.source));
}
var L5 = class extends K2 {
  constructor(e4) {
    super(), this.diagnostic = e4;
  }
  eq(e4) {
    return e4.diagnostic == this.diagnostic;
  }
  toDOM() {
    return s45("span", {
      class: "cm-lintPoint cm-lintPoint-" + this.diagnostic.severity
    });
  }
};
var x6 = class {
  constructor(e4, o4) {
    this.diagnostic = o4, this.id = "item_" + Math.floor(Math.random() * 4294967295).toString(16), this.dom = _5(e4, o4, true), this.dom.id = this.id, this.dom.setAttribute("role", "option");
  }
};
var y5 = class t4 {
  constructor(e4) {
    this.view = e4, this.items = [];
    let o4 = (n22) => {
      if (n22.keyCode == 27) I5(this.view), this.view.focus();
      else if (n22.keyCode == 38 || n22.keyCode == 33) this.moveSelection((this.selectedIndex - 1 + this.items.length) % this.items.length);
      else if (n22.keyCode == 40 || n22.keyCode == 34) this.moveSelection((this.selectedIndex + 1) % this.items.length);
      else if (n22.keyCode == 36) this.moveSelection(0);
      else if (n22.keyCode == 35) this.moveSelection(this.items.length - 1);
      else if (n22.keyCode == 13) this.view.focus();
      else if (n22.keyCode >= 65 && n22.keyCode <= 90 && this.selectedIndex >= 0) {
        let { diagnostic: s99 } = this.items[this.selectedIndex], r2 = V8(s99.actions);
        for (let l11 = 0; l11 < r2.length; l11++) if (r2[l11].toUpperCase().charCodeAt(0) == n22.keyCode) {
          let a2 = b4(this.view.state.field(d).diagnostics, s99);
          a2 && s99.actions[l11].apply(e4, a2.from, a2.to);
        }
      } else return;
      n22.preventDefault();
    }, i9 = (n22) => {
      for (let s99 = 0; s99 < this.items.length; s99++) this.items[s99].dom.contains(n22.target) && this.moveSelection(s99);
    };
    this.list = s45("ul", {
      tabIndex: 0,
      role: "listbox",
      "aria-label": this.view.state.phrase("Diagnostics"),
      onkeydown: o4,
      onclick: i9
    }), this.dom = s45("div", {
      class: "cm-panel-lint"
    }, this.list, s45("button", {
      type: "button",
      name: "close",
      "aria-label": this.view.state.phrase("close"),
      onclick: () => I5(this.view)
    }, "\xD7")), this.update();
  }
  get selectedIndex() {
    let e4 = this.view.state.field(d).selected;
    if (!e4) return -1;
    for (let o4 = 0; o4 < this.items.length; o4++) if (this.items[o4].diagnostic == e4.diagnostic) return o4;
    return -1;
  }
  update() {
    let { diagnostics: e4, selected: o4 } = this.view.state.field(d), i9 = 0, n22 = false, s99 = null;
    for (e4.between(0, this.view.state.doc.length, (r2, l11, { spec: a2 }) => {
      let c4 = -1, f2;
      for (let p5 = i9; p5 < this.items.length; p5++) if (this.items[p5].diagnostic == a2.diagnostic) {
        c4 = p5;
        break;
      }
      c4 < 0 ? (f2 = new x6(this.view, a2.diagnostic), this.items.splice(i9, 0, f2), n22 = true) : (f2 = this.items[c4], c4 > i9 && (this.items.splice(i9, c4 - i9), n22 = true)), o4 && f2.diagnostic == o4.diagnostic ? f2.dom.hasAttribute("aria-selected") || (f2.dom.setAttribute("aria-selected", "true"), s99 = f2) : f2.dom.hasAttribute("aria-selected") && f2.dom.removeAttribute("aria-selected"), i9++;
    }); i9 < this.items.length && !(this.items.length == 1 && this.items[0].diagnostic.from < 0); ) n22 = true, this.items.pop();
    this.items.length == 0 && (this.items.push(new x6(this.view, {
      from: -1,
      to: -1,
      severity: "info",
      message: this.view.state.phrase("No diagnostics")
    })), n22 = true), s99 ? (this.list.setAttribute("aria-activedescendant", s99.id), this.view.requestMeasure({
      key: this,
      read: () => ({
        sel: s99.dom.getBoundingClientRect(),
        panel: this.list.getBoundingClientRect()
      }),
      write: ({ sel: r2, panel: l11 }) => {
        r2.top < l11.top ? this.list.scrollTop -= l11.top - r2.top : r2.bottom > l11.bottom && (this.list.scrollTop += r2.bottom - l11.bottom);
      }
    })) : this.selectedIndex < 0 && this.list.removeAttribute("aria-activedescendant"), n22 && this.sync();
  }
  sync() {
    let e4 = this.list.firstChild;
    function o4() {
      let i9 = e4;
      e4 = i9.nextSibling, i9.remove();
    }
    for (let i9 of this.items) if (i9.dom.parentNode == this.list) {
      for (; e4 != i9.dom; ) o4();
      e4 = i9.dom.nextSibling;
    } else this.list.insertBefore(i9.dom, e4);
    for (; e4; ) o4();
  }
  moveSelection(e4) {
    if (this.selectedIndex < 0) return;
    let o4 = this.view.state.field(d), i9 = b4(o4.diagnostics, this.items[e4].diagnostic);
    i9 && this.view.dispatch({
      selection: {
        anchor: i9.from,
        head: i9.to
      },
      scrollIntoView: true,
      effects: $4.of(i9)
    });
  }
  static open(e4) {
    return new t4(e4);
  }
};
function k5(t5, e4 = 'viewBox="0 0 40 40"') {
  return `url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" ${e4}>${encodeURIComponent(t5)}</svg>')`;
}
function P5(t5) {
  return k5(`<path d="m0 2.5 l2 -1.5 l1 0 l2 1.5 l1 0" stroke="${t5}" fill="none" stroke-width=".7"/>`, 'width="6" height="3"');
}
var le5 = M2.baseTheme({
  ".cm-diagnostic": {
    padding: "3px 6px 3px 8px",
    marginLeft: "-1px",
    display: "block",
    whiteSpace: "pre-wrap"
  },
  ".cm-diagnostic-error": {
    borderLeft: "5px solid #d11"
  },
  ".cm-diagnostic-warning": {
    borderLeft: "5px solid orange"
  },
  ".cm-diagnostic-info": {
    borderLeft: "5px solid #999"
  },
  ".cm-diagnosticAction": {
    font: "inherit",
    border: "none",
    padding: "2px 4px",
    backgroundColor: "#444",
    color: "white",
    borderRadius: "3px",
    marginLeft: "8px"
  },
  ".cm-diagnosticSource": {
    fontSize: "70%",
    opacity: 0.7
  },
  ".cm-lintRange": {
    backgroundPosition: "left bottom",
    backgroundRepeat: "repeat-x",
    paddingBottom: "0.7px"
  },
  ".cm-lintRange-error": {
    backgroundImage: P5("#d11")
  },
  ".cm-lintRange-warning": {
    backgroundImage: P5("orange")
  },
  ".cm-lintRange-info": {
    backgroundImage: P5("#999")
  },
  ".cm-lintRange-active": {
    backgroundColor: "#ffdd9980"
  },
  ".cm-tooltip-lint": {
    padding: 0,
    margin: 0
  },
  ".cm-lintPoint": {
    position: "relative",
    "&:after": {
      content: '""',
      position: "absolute",
      bottom: 0,
      left: "-2px",
      borderLeft: "3px solid transparent",
      borderRight: "3px solid transparent",
      borderBottom: "4px solid #d11"
    }
  },
  ".cm-lintPoint-warning": {
    "&:after": {
      borderBottomColor: "orange"
    }
  },
  ".cm-lintPoint-info": {
    "&:after": {
      borderBottomColor: "#999"
    }
  },
  ".cm-panel.cm-panel-lint": {
    position: "relative",
    "& ul": {
      maxHeight: "100px",
      overflowY: "auto",
      "& [aria-selected]": {
        backgroundColor: "#ddd",
        "& u": {
          textDecoration: "underline"
        }
      },
      "&:focus [aria-selected]": {
        background_fallback: "#bdf",
        backgroundColor: "Highlight",
        color_fallback: "white",
        color: "HighlightText"
      },
      "& u": {
        textDecoration: "none"
      },
      padding: 0,
      margin: 0
    },
    "& [name=close]": {
      position: "absolute",
      top: "0",
      right: "2px",
      background: "inherit",
      border: "none",
      font: "inherit",
      padding: 0,
      margin: 0
    }
  }
});
var A7 = class extends I2 {
  constructor(e4) {
    super(), this.diagnostics = e4, this.severity = e4.reduce((o4, i9) => {
      let n22 = i9.severity;
      return n22 == "error" || n22 == "warning" && o4 == "info" ? n22 : o4;
    }, "info");
  }
  toDOM(e4) {
    let o4 = document.createElement("div");
    o4.className = "cm-lint-marker cm-lint-marker-" + this.severity;
    let i9 = this.diagnostics, n22 = e4.state.facet(T5).tooltipFilter;
    return n22 && (i9 = n22(i9)), i9.length && (o4.onmouseover = () => ae6(e4, o4, i9)), o4;
  }
};
function re6(t5, e4) {
  let o4 = (i9) => {
    let n22 = e4.getBoundingClientRect();
    if (!(i9.clientX > n22.left - 10 && i9.clientX < n22.right + 10 && i9.clientY > n22.top - 10 && i9.clientY < n22.bottom + 10)) {
      for (let s99 = i9.target; s99; s99 = s99.parentNode) if (s99.nodeType == 1 && s99.classList.contains("cm-tooltip-lint")) return;
      globalThis.removeEventListener("mousemove", o4), t5.state.field(z6) && t5.dispatch({
        effects: M7.of(null)
      });
    }
  };
  globalThis.addEventListener("mousemove", o4);
}
function ae6(t5, e4, o4) {
  function i9() {
    let r2 = t5.elementAtHeight(e4.getBoundingClientRect().top + 5 - t5.documentTop);
    t5.coordsAtPos(r2.from) && t5.dispatch({
      effects: M7.of({
        pos: r2.from,
        above: false,
        create() {
          return {
            dom: H5(t5, o4),
            getCoords: () => e4.getBoundingClientRect()
          };
        }
      })
    }), e4.onmouseout = e4.onmousemove = null, re6(t5, e4);
  }
  let { hoverTime: n22 } = t5.state.facet(T5), s99 = setTimeout(i9, n22);
  e4.onmouseout = () => {
    clearTimeout(s99), e4.onmouseout = e4.onmousemove = null;
  }, e4.onmousemove = () => {
    clearTimeout(s99), s99 = setTimeout(i9, n22);
  };
}
function ce7(t5, e4) {
  let o4 = /* @__PURE__ */ Object.create(null);
  for (let n22 of e4) {
    let s99 = t5.lineAt(n22.from);
    (o4[s99.from] || (o4[s99.from] = [])).push(n22);
  }
  let i9 = [];
  for (let n22 in o4) i9.push(new A7(o4[n22]).range(+n22));
  return O.of(i9, true);
}
var de6 = mo({
  class: "cm-gutter-lint",
  markers: (t5) => t5.state.field(q5)
});
var q5 = $.define({
  create() {
    return O.empty;
  },
  update(t5, e4) {
    t5 = t5.map(e4.changes);
    let o4 = e4.state.facet(T5).markerFilter;
    for (let i9 of e4.effects) if (i9.is(C7)) {
      let n22 = i9.value;
      o4 && (n22 = o4(n22 || [])), t5 = ce7(e4.state.doc, n22.slice(0));
    }
    return t5;
  }
});
var M7 = v.define();
var z6 = $.define({
  create() {
    return null;
  },
  update(t5, e4) {
    return t5 && e4.docChanged && (t5 = j5(e4, t5) ? null : Object.assign(Object.assign({}, t5), {
      pos: e4.changes.mapPos(t5.pos)
    })), e4.effects.reduce((o4, i9) => i9.is(M7) ? i9.value : o4, t5);
  },
  provide: (t5) => rn.from(t5)
});
var fe5 = M2.baseTheme({
  ".cm-gutter-lint": {
    width: "1.4em",
    "& .cm-gutterElement": {
      padding: ".2em"
    }
  },
  ".cm-lint-marker": {
    width: "1em",
    height: "1em"
  },
  ".cm-lint-marker-info": {
    content: k5('<path fill="#aaf" stroke="#77e" stroke-width="6" stroke-linejoin="round" d="M5 5L35 5L35 35L5 35Z"/>')
  },
  ".cm-lint-marker-warning": {
    content: k5('<path fill="#fe8" stroke="#fd7" stroke-width="6" stroke-linejoin="round" d="M20 6L37 35L3 35Z"/>')
  },
  ".cm-lint-marker-error:before": {
    content: k5('<circle cx="20" cy="20" r="15" fill="#f87" stroke="#f43" stroke-width="6"/>')
  }
});
var T5 = y.define({
  combine(t5) {
    return ht(t5, {
      hoverTime: 300,
      markerFilter: null,
      tooltipFilter: null
    });
  }
});

// deno:https://esm.sh/@codemirror/search@0.20.1/denonext/search.mjs
var Y6 = typeof String.prototype.normalize == "function" ? (n22) => n22.normalize("NFKD") : (n22) => n22;
var b5 = class {
  constructor(e4, t5, r2 = 0, s99 = e4.length, i9) {
    this.value = {
      from: 0,
      to: 0
    }, this.done = false, this.matches = [], this.buffer = "", this.bufferPos = 0, this.iter = e4.iterRange(r2, s99), this.bufferStart = r2, this.normalize = i9 ? (a2) => i9(Y6(a2)) : Y6, this.query = this.normalize(t5);
  }
  peek() {
    if (this.bufferPos == this.buffer.length) {
      if (this.bufferStart += this.buffer.length, this.iter.next(), this.iter.done) return -1;
      this.bufferPos = 0, this.buffer = this.iter.value;
    }
    return he(this.buffer, this.bufferPos);
  }
  next() {
    for (; this.matches.length; ) this.matches.pop();
    return this.nextOverlapping();
  }
  nextOverlapping() {
    for (; ; ) {
      let e4 = this.peek();
      if (e4 < 0) return this.done = true, this;
      let t5 = rt(e4), r2 = this.bufferStart + this.bufferPos;
      this.bufferPos += be(e4);
      let s99 = this.normalize(t5);
      for (let i9 = 0, a2 = r2; ; i9++) {
        let l11 = s99.charCodeAt(i9), c4 = this.match(l11, a2);
        if (c4) return this.value = c4, this;
        if (i9 == s99.length - 1) break;
        a2 == r2 && i9 < t5.length && t5.charCodeAt(i9) == l11 && a2++;
      }
    }
  }
  match(e4, t5) {
    let r2 = null;
    for (let s99 = 0; s99 < this.matches.length; s99 += 2) {
      let i9 = this.matches[s99], a2 = false;
      this.query.charCodeAt(i9) == e4 && (i9 == this.query.length - 1 ? r2 = {
        from: this.matches[s99 + 1],
        to: t5 + 1
      } : (this.matches[s99]++, a2 = true)), a2 || (this.matches.splice(s99, 2), s99 -= 2);
    }
    return this.query.charCodeAt(0) == e4 && (this.query.length == 1 ? r2 = {
      from: t5,
      to: t5 + 1
    } : this.matches.push(1, t5)), r2;
  }
};
typeof Symbol < "u" && (b5.prototype[Symbol.iterator] = function() {
  return this;
});
var le6 = {
  from: -1,
  to: -1,
  match: /.*/.exec("")
};
var Q7 = "gm" + (/x/.unicode == null ? "" : "u");
var q6 = class {
  constructor(e4, t5, r2, s99 = 0, i9 = e4.length) {
    if (this.to = i9, this.curLine = "", this.done = false, this.value = le6, /\\[sWDnr]|\n|\r|\[\^/.test(t5)) return new R7(e4, t5, r2, s99, i9);
    this.re = new RegExp(t5, Q7 + (r2?.ignoreCase ? "i" : "")), this.iter = e4.iter();
    let a2 = e4.lineAt(s99);
    this.curLineStart = a2.from, this.matchPos = s99, this.getLine(this.curLineStart);
  }
  getLine(e4) {
    this.iter.next(e4), this.iter.lineBreak ? this.curLine = "" : (this.curLine = this.iter.value, this.curLineStart + this.curLine.length > this.to && (this.curLine = this.curLine.slice(0, this.to - this.curLineStart)), this.iter.next());
  }
  nextLine() {
    this.curLineStart = this.curLineStart + this.curLine.length + 1, this.curLineStart > this.to ? this.curLine = "" : this.getLine(0);
  }
  next() {
    for (let e4 = this.matchPos - this.curLineStart; ; ) {
      this.re.lastIndex = e4;
      let t5 = this.matchPos <= this.to && this.re.exec(this.curLine);
      if (t5) {
        let r2 = this.curLineStart + t5.index, s99 = r2 + t5[0].length;
        if (this.matchPos = s99 + (r2 == s99 ? 1 : 0), r2 == this.curLine.length && this.nextLine(), r2 < s99 || r2 > this.value.to) return this.value = {
          from: r2,
          to: s99,
          match: t5
        }, this;
        e4 = this.matchPos - this.curLineStart;
      } else if (this.curLineStart + this.curLine.length < this.to) this.nextLine(), e4 = 0;
      else return this.done = true, this;
    }
  }
};
var N8 = /* @__PURE__ */ new WeakMap();
var E5 = class n11 {
  constructor(e4, t5) {
    this.from = e4, this.text = t5;
  }
  get to() {
    return this.from + this.text.length;
  }
  static get(e4, t5, r2) {
    let s99 = N8.get(e4);
    if (!s99 || s99.from >= r2 || s99.to <= t5) {
      let l11 = new n11(t5, e4.sliceString(t5, r2));
      return N8.set(e4, l11), l11;
    }
    if (s99.from == t5 && s99.to == r2) return s99;
    let { text: i9, from: a2 } = s99;
    return a2 > t5 && (i9 = e4.sliceString(t5, a2) + i9, a2 = t5), s99.to < r2 && (i9 += e4.sliceString(s99.to, r2)), N8.set(e4, new n11(a2, i9)), new n11(t5, i9.slice(t5 - a2, r2 - a2));
  }
};
var R7 = class {
  constructor(e4, t5, r2, s99, i9) {
    this.text = e4, this.to = i9, this.done = false, this.value = le6, this.matchPos = s99, this.re = new RegExp(t5, Q7 + (r2?.ignoreCase ? "i" : "")), this.flat = E5.get(e4, s99, this.chunkEnd(s99 + 5e3));
  }
  chunkEnd(e4) {
    return e4 >= this.to ? this.to : this.text.lineAt(e4).to;
  }
  next() {
    for (; ; ) {
      let e4 = this.re.lastIndex = this.matchPos - this.flat.from, t5 = this.re.exec(this.flat.text);
      if (t5 && !t5[0] && t5.index == e4 && (this.re.lastIndex = e4 + 1, t5 = this.re.exec(this.flat.text)), t5 && this.flat.to < this.to && t5.index + t5[0].length > this.flat.text.length - 10 && (t5 = null), t5) {
        let r2 = this.flat.from + t5.index, s99 = r2 + t5[0].length;
        return this.value = {
          from: r2,
          to: s99,
          match: t5
        }, this.matchPos = s99 + (r2 == s99 ? 1 : 0), this;
      } else {
        if (this.flat.to == this.to) return this.done = true, this;
        this.flat = E5.get(this.text, this.flat.from, this.chunkEnd(this.flat.from + this.flat.text.length * 2));
      }
    }
  }
};
typeof Symbol < "u" && (q6.prototype[Symbol.iterator] = R7.prototype[Symbol.iterator] = function() {
  return this;
});
function xe6(n22) {
  try {
    return new RegExp(n22, Q7), true;
  } catch {
    return false;
  }
}
function B7(n22) {
  let e4 = s45("input", {
    class: "cm-textfield",
    name: "line"
  }), t5 = s45("form", {
    class: "cm-gotoLine",
    onkeydown: (s99) => {
      s99.keyCode == 27 ? (s99.preventDefault(), n22.dispatch({
        effects: I6.of(false)
      }), n22.focus()) : s99.keyCode == 13 && (s99.preventDefault(), r2());
    },
    onsubmit: (s99) => {
      s99.preventDefault(), r2();
    }
  }, s45("label", n22.state.phrase("Go to line"), ": ", e4), " ", s45("button", {
    class: "cm-button",
    type: "submit"
  }, n22.state.phrase("go")));
  function r2() {
    let s99 = /^([+-])?(\d+)?(:\d+)?(%)?$/.exec(e4.value);
    if (!s99) return;
    let { state: i9 } = n22, a2 = i9.doc.lineAt(i9.selection.main.head), [, l11, c4, f2, d5] = s99, m9 = f2 ? +f2.slice(1) : 0, g6 = c4 ? +c4 : a2.number;
    if (c4 && d5) {
      let V13 = g6 / 100;
      l11 && (V13 = V13 * (l11 == "-" ? -1 : 1) + a2.number / i9.doc.lines), g6 = Math.round(i9.doc.lines * V13);
    } else c4 && l11 && (g6 = g6 * (l11 == "-" ? -1 : 1) + a2.number);
    let X14 = i9.doc.line(Math.max(1, Math.min(i9.doc.lines, g6)));
    n22.dispatch({
      effects: I6.of(false),
      selection: x.cursor(X14.from + Math.max(0, Math.min(m9, X14.length))),
      scrollIntoView: true
    }), n22.focus();
  }
  return {
    dom: t5
  };
}
var I6 = v.define();
var Z8 = $.define({
  create() {
    return true;
  },
  update(n22, e4) {
    for (let t5 of e4.effects) t5.is(I6) && (n22 = t5.value);
    return n22;
  },
  provide: (n22) => ns.from(n22, (e4) => e4 ? B7 : null)
});
var be5 = (n22) => {
  let e4 = po(n22, B7);
  if (!e4) {
    let t5 = [
      I6.of(true)
    ];
    n22.state.field(Z8, false) == null && t5.push(v.appendConfig.of([
      Z8,
      ye5
    ])), n22.dispatch({
      effects: t5
    }), e4 = po(n22, B7);
  }
  return e4 && e4.dom.querySelector("input").focus(), true;
};
var ye5 = M2.baseTheme({
  ".cm-panel.cm-gotoLine": {
    padding: "2px 6px 4px",
    "& label": {
      fontSize: "80%"
    }
  }
});
var Se6 = {
  highlightWordAroundCursor: false,
  minSelectionLength: 1,
  maxMatches: 100,
  wholeWords: false
};
var ae7 = y.define({
  combine(n22) {
    return ht(n22, Se6, {
      highlightWordAroundCursor: (e4, t5) => e4 || t5,
      minSelectionLength: Math.min,
      maxMatches: Math.min
    });
  }
});
function Te6(n22) {
  let e4 = [
    Le6,
    Ce6
  ];
  return n22 && e4.push(ae7.of(n22)), e4;
}
var Me5 = C2.mark({
  class: "cm-selectionMatch"
});
var ve5 = C2.mark({
  class: "cm-selectionMatch cm-selectionMatch-main"
});
function ee5(n22, e4, t5, r2) {
  return (t5 == 0 || n22(e4.sliceDoc(t5 - 1, t5)) != E.Word) && (r2 == e4.doc.length || n22(e4.sliceDoc(r2, r2 + 1)) != E.Word);
}
function ke6(n22, e4, t5, r2) {
  return n22(e4.sliceDoc(t5, t5 + 1)) == E.Word && n22(e4.sliceDoc(r2 - 1, r2)) == E.Word;
}
var Ce6 = P2.fromClass(class {
  constructor(n22) {
    this.decorations = this.getDeco(n22);
  }
  update(n22) {
    (n22.selectionSet || n22.docChanged || n22.viewportChanged) && (this.decorations = this.getDeco(n22.view));
  }
  getDeco(n22) {
    let e4 = n22.state.facet(ae7), { state: t5 } = n22, r2 = t5.selection;
    if (r2.ranges.length > 1) return C2.none;
    let s99 = r2.main, i9, a2 = null;
    if (s99.empty) {
      if (!e4.highlightWordAroundCursor) return C2.none;
      let c4 = t5.wordAt(s99.head);
      if (!c4) return C2.none;
      a2 = t5.charCategorizer(s99.head), i9 = t5.sliceDoc(c4.from, c4.to);
    } else {
      let c4 = s99.to - s99.from;
      if (c4 < e4.minSelectionLength || c4 > 200) return C2.none;
      if (e4.wholeWords) {
        if (i9 = t5.sliceDoc(s99.from, s99.to), a2 = t5.charCategorizer(s99.head), !(ee5(a2, t5, s99.from, s99.to) && ke6(a2, t5, s99.from, s99.to))) return C2.none;
      } else if (i9 = t5.sliceDoc(s99.from, s99.to).trim(), !i9) return C2.none;
    }
    let l11 = [];
    for (let c4 of n22.visibleRanges) {
      let f2 = new b5(t5.doc, i9, c4.from, c4.to);
      for (; !f2.next().done; ) {
        let { from: d5, to: m9 } = f2.value;
        if ((!a2 || ee5(a2, t5, d5, m9)) && (s99.empty && d5 <= s99.from && m9 >= s99.to ? l11.push(ve5.range(d5, m9)) : (d5 >= s99.to || m9 <= s99.from) && l11.push(Me5.range(d5, m9)), l11.length > e4.maxMatches)) return C2.none;
      }
    }
    return C2.set(l11);
  }
}, {
  decorations: (n22) => n22.decorations
});
var Le6 = M2.baseTheme({
  ".cm-selectionMatch": {
    backgroundColor: "#99ff7780"
  },
  ".cm-searchMatch .cm-selectionMatch": {
    backgroundColor: "transparent"
  }
});
var De6 = ({ state: n22, dispatch: e4 }) => {
  let { selection: t5 } = n22, r2 = x.create(t5.ranges.map((s99) => n22.wordAt(s99.head) || x.cursor(s99.head)), t5.mainIndex);
  return r2.eq(t5) ? false : (e4(n22.update({
    selection: r2
  })), true);
};
function Pe6(n22, e4) {
  let { main: t5, ranges: r2 } = n22.selection, s99 = n22.wordAt(t5.head), i9 = s99 && s99.from == t5.from && s99.to == t5.to;
  for (let a2 = false, l11 = new b5(n22.doc, e4, r2[r2.length - 1].to); ; ) if (l11.next(), l11.done) {
    if (a2) return null;
    l11 = new b5(n22.doc, e4, 0, Math.max(0, r2[r2.length - 1].from - 1)), a2 = true;
  } else {
    if (a2 && r2.some((c4) => c4.from == l11.value.from)) continue;
    if (i9) {
      let c4 = n22.wordAt(l11.value.from);
      if (!c4 || c4.from != l11.value.from || c4.to != l11.value.to) continue;
    }
    return l11.value;
  }
}
var Fe5 = ({ state: n22, dispatch: e4 }) => {
  let { ranges: t5 } = n22.selection;
  if (t5.some((i9) => i9.from === i9.to)) return De6({
    state: n22,
    dispatch: e4
  });
  let r2 = n22.sliceDoc(t5[0].from, t5[0].to);
  if (n22.selection.ranges.some((i9) => n22.sliceDoc(i9.from, i9.to) != r2)) return false;
  let s99 = Pe6(n22, r2);
  return s99 ? (e4(n22.update({
    selection: n22.selection.addRange(x.range(s99.from, s99.to), false),
    effects: M2.scrollIntoView(s99.to)
  })), true) : false;
};
var T6 = y.define({
  combine(n22) {
    var e4;
    return {
      top: n22.reduce((t5, r2) => t5 ?? r2.top, void 0) || false,
      caseSensitive: n22.reduce((t5, r2) => t5 ?? r2.caseSensitive, void 0) || false,
      createPanel: ((e4 = n22.find((t5) => t5.createPanel)) === null || e4 === void 0 ? void 0 : e4.createPanel) || ((t5) => new _6(t5))
    };
  }
});
var W6 = class {
  constructor(e4) {
    this.search = e4.search, this.caseSensitive = !!e4.caseSensitive, this.regexp = !!e4.regexp, this.replace = e4.replace || "", this.valid = !!this.search && (!this.regexp || xe6(this.search)), this.unquoted = e4.literal ? this.search : this.search.replace(/\\([nrt\\])/g, (t5, r2) => r2 == "n" ? `
` : r2 == "r" ? "\r" : r2 == "t" ? "	" : "\\");
  }
  eq(e4) {
    return this.search == e4.search && this.replace == e4.replace && this.caseSensitive == e4.caseSensitive && this.regexp == e4.regexp;
  }
  create() {
    return this.regexp ? new K7(this) : new H6(this);
  }
  getCursor(e4, t5 = 0, r2 = e4.length) {
    return this.regexp ? S6(this, e4, t5, r2) : y6(this, e4, t5, r2);
  }
};
var z7 = class {
  constructor(e4) {
    this.spec = e4;
  }
};
function y6(n22, e4, t5, r2) {
  return new b5(e4, n22.unquoted, t5, r2, n22.caseSensitive ? void 0 : (s99) => s99.toLowerCase());
}
var H6 = class extends z7 {
  constructor(e4) {
    super(e4);
  }
  nextMatch(e4, t5, r2) {
    let s99 = y6(this.spec, e4, r2, e4.length).nextOverlapping();
    return s99.done && (s99 = y6(this.spec, e4, 0, t5).nextOverlapping()), s99.done ? null : s99.value;
  }
  prevMatchInRange(e4, t5, r2) {
    for (let s99 = r2; ; ) {
      let i9 = Math.max(t5, s99 - 1e4 - this.spec.unquoted.length), a2 = y6(this.spec, e4, i9, s99), l11 = null;
      for (; !a2.nextOverlapping().done; ) l11 = a2.value;
      if (l11) return l11;
      if (i9 == t5) return null;
      s99 -= 1e4;
    }
  }
  prevMatch(e4, t5, r2) {
    return this.prevMatchInRange(e4, 0, t5) || this.prevMatchInRange(e4, r2, e4.length);
  }
  getReplacement(e4) {
    return this.spec.replace;
  }
  matchAll(e4, t5) {
    let r2 = y6(this.spec, e4, 0, e4.length), s99 = [];
    for (; !r2.next().done; ) {
      if (s99.length >= t5) return null;
      s99.push(r2.value);
    }
    return s99;
  }
  highlight(e4, t5, r2, s99) {
    let i9 = y6(this.spec, e4, Math.max(0, t5 - this.spec.unquoted.length), Math.min(r2 + this.spec.unquoted.length, e4.length));
    for (; !i9.next().done; ) s99(i9.value.from, i9.value.to);
  }
};
function S6(n22, e4, t5, r2) {
  return new q6(e4, n22.search, n22.caseSensitive ? void 0 : {
    ignoreCase: true
  }, t5, r2);
}
var K7 = class extends z7 {
  nextMatch(e4, t5, r2) {
    let s99 = S6(this.spec, e4, r2, e4.length).next();
    return s99.done && (s99 = S6(this.spec, e4, 0, t5).next()), s99.done ? null : s99.value;
  }
  prevMatchInRange(e4, t5, r2) {
    for (let s99 = 1; ; s99++) {
      let i9 = Math.max(t5, r2 - s99 * 1e4), a2 = S6(this.spec, e4, i9, r2), l11 = null;
      for (; !a2.next().done; ) l11 = a2.value;
      if (l11 && (i9 == t5 || l11.from > i9 + 10)) return l11;
      if (i9 == t5) return null;
    }
  }
  prevMatch(e4, t5, r2) {
    return this.prevMatchInRange(e4, 0, t5) || this.prevMatchInRange(e4, r2, e4.length);
  }
  getReplacement(e4) {
    return this.spec.replace.replace(/\$([$&\d+])/g, (t5, r2) => r2 == "$" ? "$" : r2 == "&" ? e4.match[0] : r2 != "0" && +r2 < e4.match.length ? e4.match[r2] : t5);
  }
  matchAll(e4, t5) {
    let r2 = S6(this.spec, e4, 0, e4.length), s99 = [];
    for (; !r2.next().done; ) {
      if (s99.length >= t5) return null;
      s99.push(r2.value);
    }
    return s99;
  }
  highlight(e4, t5, r2, s99) {
    let i9 = S6(this.spec, e4, Math.max(0, t5 - 250), Math.min(r2 + 250, e4.length));
    for (; !i9.next().done; ) s99(i9.value.from, i9.value.to);
  }
};
var v4 = v.define();
var j6 = v.define();
var p3 = $.define({
  create(n22) {
    return new M8(w6(n22).create(), null);
  },
  update(n22, e4) {
    for (let t5 of e4.effects) t5.is(v4) ? n22 = new M8(t5.value.create(), n22.panel) : t5.is(j6) && (n22 = new M8(n22.query, t5.value ? J5 : null));
    return n22;
  },
  provide: (n22) => ns.from(n22, (e4) => e4.panel)
});
var M8 = class {
  constructor(e4, t5) {
    this.query = e4, this.panel = t5;
  }
};
var Ae4 = C2.mark({
  class: "cm-searchMatch"
});
var qe4 = C2.mark({
  class: "cm-searchMatch cm-searchMatch-selected"
});
var Ee4 = P2.fromClass(class {
  constructor(n22) {
    this.view = n22, this.decorations = this.highlight(n22.state.field(p3));
  }
  update(n22) {
    let e4 = n22.state.field(p3);
    (e4 != n22.startState.field(p3) || n22.docChanged || n22.selectionSet || n22.viewportChanged) && (this.decorations = this.highlight(e4));
  }
  highlight({ query: n22, panel: e4 }) {
    if (!e4 || !n22.spec.valid) return C2.none;
    let { view: t5 } = this, r2 = new se();
    for (let s99 = 0, i9 = t5.visibleRanges, a2 = i9.length; s99 < a2; s99++) {
      let { from: l11, to: c4 } = i9[s99];
      for (; s99 < a2 - 1 && c4 > i9[s99 + 1].from - 500; ) c4 = i9[++s99].to;
      n22.highlight(t5.state.doc, l11, c4, (f2, d5) => {
        let m9 = t5.state.selection.ranges.some((g6) => g6.from == f2 && g6.to == d5);
        r2.add(f2, d5, m9 ? qe4 : Ae4);
      });
    }
    return r2.finish();
  }
}, {
  decorations: (n22) => n22.decorations
});
function L6(n22) {
  return (e4) => {
    let t5 = e4.state.field(p3, false);
    return t5 && t5.query.spec.valid ? n22(e4, t5) : ce8(e4);
  };
}
var O5 = L6((n22, { query: e4 }) => {
  let { from: t5, to: r2 } = n22.state.selection.main, s99 = e4.nextMatch(n22.state.doc, t5, r2);
  return !s99 || s99.from == t5 && s99.to == r2 ? false : (n22.dispatch({
    selection: {
      anchor: s99.from,
      head: s99.to
    },
    scrollIntoView: true,
    effects: U7(n22, s99),
    userEvent: "select.search"
  }), true);
});
var $5 = L6((n22, { query: e4 }) => {
  let { state: t5 } = n22, { from: r2, to: s99 } = t5.selection.main, i9 = e4.prevMatch(t5.doc, r2, s99);
  return i9 ? (n22.dispatch({
    selection: {
      anchor: i9.from,
      head: i9.to
    },
    scrollIntoView: true,
    effects: U7(n22, i9),
    userEvent: "select.search"
  }), true) : false;
});
var Re5 = L6((n22, { query: e4 }) => {
  let t5 = e4.matchAll(n22.state.doc, 1e3);
  return !t5 || !t5.length ? false : (n22.dispatch({
    selection: x.create(t5.map((r2) => x.range(r2.from, r2.to))),
    userEvent: "select.search.matches"
  }), true);
});
var Ie5 = ({ state: n22, dispatch: e4 }) => {
  let t5 = n22.selection;
  if (t5.ranges.length > 1 || t5.main.empty) return false;
  let { from: r2, to: s99 } = t5.main, i9 = [], a2 = 0;
  for (let l11 = new b5(n22.doc, n22.sliceDoc(r2, s99)); !l11.next().done; ) {
    if (i9.length > 1e3) return false;
    l11.value.from == r2 && (a2 = i9.length), i9.push(x.range(l11.value.from, l11.value.to));
  }
  return e4(n22.update({
    selection: x.create(i9, a2),
    userEvent: "select.search.matches"
  })), true;
};
var te6 = L6((n22, { query: e4 }) => {
  let { state: t5 } = n22, { from: r2, to: s99 } = t5.selection.main;
  if (t5.readOnly) return false;
  let i9 = e4.nextMatch(t5.doc, r2, r2);
  if (!i9) return false;
  let a2 = [], l11, c4;
  if (i9.from == r2 && i9.to == s99 && (c4 = t5.toText(e4.getReplacement(i9)), a2.push({
    from: i9.from,
    to: i9.to,
    insert: c4
  }), i9 = e4.nextMatch(t5.doc, i9.from, i9.to)), i9) {
    let f2 = a2.length == 0 || a2[0].from >= i9.to ? 0 : i9.to - i9.from - c4.length;
    l11 = {
      anchor: i9.from - f2,
      head: i9.to - f2
    };
  }
  return n22.dispatch({
    changes: a2,
    selection: l11,
    scrollIntoView: !!l11,
    effects: i9 ? U7(n22, i9) : void 0,
    userEvent: "input.replace"
  }), true;
});
var We4 = L6((n22, { query: e4 }) => {
  if (n22.state.readOnly) return false;
  let t5 = e4.matchAll(n22.state.doc, 1e9).map((r2) => {
    let { from: s99, to: i9 } = r2;
    return {
      from: s99,
      to: i9,
      insert: e4.getReplacement(r2)
    };
  });
  return t5.length ? (n22.dispatch({
    changes: t5,
    userEvent: "input.replace.all"
  }), true) : false;
});
function J5(n22) {
  return n22.state.facet(T6).createPanel(n22);
}
function w6(n22, e4) {
  var t5;
  let r2 = n22.selection.main, s99 = r2.empty || r2.to > r2.from + 100 ? "" : n22.sliceDoc(r2.from, r2.to), i9 = (t5 = e4?.caseSensitive) !== null && t5 !== void 0 ? t5 : n22.facet(T6).caseSensitive;
  return e4 && !s99 ? e4 : new W6({
    search: s99.replace(/\n/g, "\\n"),
    caseSensitive: i9
  });
}
var ce8 = (n22) => {
  let e4 = n22.state.field(p3, false);
  if (e4 && e4.panel) {
    let t5 = po(n22, J5);
    if (!t5) return false;
    let r2 = t5.dom.querySelector("[name=search]");
    if (r2 != n22.root.activeElement) {
      let s99 = w6(n22.state, e4.query.spec);
      s99.valid && n22.dispatch({
        effects: v4.of(s99)
      }), r2.focus(), r2.select();
    }
  } else n22.dispatch({
    effects: [
      j6.of(true),
      e4 ? v4.of(w6(n22.state, e4.query.spec)) : v.appendConfig.of(G5)
    ]
  });
  return true;
};
var oe7 = (n22) => {
  let e4 = n22.state.field(p3, false);
  if (!e4 || !e4.panel) return false;
  let t5 = po(n22, J5);
  return t5 && t5.dom.contains(n22.root.activeElement) && n22.focus(), n22.dispatch({
    effects: j6.of(false)
  }), true;
};
var Be5 = [
  {
    key: "Mod-f",
    run: ce8,
    scope: "editor search-panel"
  },
  {
    key: "F3",
    run: O5,
    shift: $5,
    scope: "editor search-panel",
    preventDefault: true
  },
  {
    key: "Mod-g",
    run: O5,
    shift: $5,
    scope: "editor search-panel",
    preventDefault: true
  },
  {
    key: "Escape",
    run: oe7,
    scope: "editor search-panel"
  },
  {
    key: "Mod-Shift-l",
    run: Ie5
  },
  {
    key: "Alt-g",
    run: be5
  },
  {
    key: "Mod-d",
    run: Fe5,
    preventDefault: true
  }
];
var _6 = class {
  constructor(e4) {
    this.view = e4;
    let t5 = this.query = e4.state.field(p3).query.spec;
    this.commit = this.commit.bind(this), this.searchField = s45("input", {
      value: t5.search,
      placeholder: u2(e4, "Find"),
      "aria-label": u2(e4, "Find"),
      class: "cm-textfield",
      name: "search",
      onchange: this.commit,
      onkeyup: this.commit
    }), this.replaceField = s45("input", {
      value: t5.replace,
      placeholder: u2(e4, "Replace"),
      "aria-label": u2(e4, "Replace"),
      class: "cm-textfield",
      name: "replace",
      onchange: this.commit,
      onkeyup: this.commit
    }), this.caseField = s45("input", {
      type: "checkbox",
      name: "case",
      checked: t5.caseSensitive,
      onchange: this.commit
    }), this.reField = s45("input", {
      type: "checkbox",
      name: "re",
      checked: t5.regexp,
      onchange: this.commit
    });
    function r2(s99, i9, a2) {
      return s45("button", {
        class: "cm-button",
        name: s99,
        onclick: i9,
        type: "button"
      }, a2);
    }
    this.dom = s45("div", {
      onkeydown: (s99) => this.keydown(s99),
      class: "cm-search"
    }, [
      this.searchField,
      r2("next", () => O5(e4), [
        u2(e4, "next")
      ]),
      r2("prev", () => $5(e4), [
        u2(e4, "previous")
      ]),
      r2("select", () => Re5(e4), [
        u2(e4, "all")
      ]),
      s45("label", null, [
        this.caseField,
        u2(e4, "match case")
      ]),
      s45("label", null, [
        this.reField,
        u2(e4, "regexp")
      ]),
      ...e4.state.readOnly ? [] : [
        s45("br"),
        this.replaceField,
        r2("replace", () => te6(e4), [
          u2(e4, "replace")
        ]),
        r2("replaceAll", () => We4(e4), [
          u2(e4, "replace all")
        ]),
        s45("button", {
          name: "close",
          onclick: () => oe7(e4),
          "aria-label": u2(e4, "close"),
          type: "button"
        }, [
          "\xD7"
        ])
      ]
    ]);
  }
  commit() {
    let e4 = new W6({
      search: this.searchField.value,
      caseSensitive: this.caseField.checked,
      regexp: this.reField.checked,
      replace: this.replaceField.value
    });
    e4.eq(this.query) || (this.query = e4, this.view.dispatch({
      effects: v4.of(e4)
    }));
  }
  keydown(e4) {
    Jr(this.view, e4, "search-panel") ? e4.preventDefault() : e4.keyCode == 13 && e4.target == this.searchField ? (e4.preventDefault(), (e4.shiftKey ? $5 : O5)(this.view)) : e4.keyCode == 13 && e4.target == this.replaceField && (e4.preventDefault(), te6(this.view));
  }
  update(e4) {
    for (let t5 of e4.transactions) for (let r2 of t5.effects) r2.is(v4) && !r2.value.eq(this.query) && this.setQuery(r2.value);
  }
  setQuery(e4) {
    this.query = e4, this.searchField.value = e4.search, this.replaceField.value = e4.replace, this.caseField.checked = e4.caseSensitive, this.reField.checked = e4.regexp;
  }
  mount() {
    this.searchField.select();
  }
  get pos() {
    return 80;
  }
  get top() {
    return this.view.state.facet(T6).top;
  }
};
function u2(n22, e4) {
  return n22.state.phrase(e4);
}
var D5 = 30;
var P6 = /[\s\.,:;?!]/;
function U7(n22, { from: e4, to: t5 }) {
  let r2 = n22.state.doc.lineAt(e4).from, s99 = n22.state.doc.lineAt(t5).to, i9 = Math.max(r2, e4 - D5), a2 = Math.min(s99, t5 + D5), l11 = n22.state.sliceDoc(i9, a2);
  if (i9 != r2) {
    for (let c4 = 0; c4 < D5; c4++) if (!P6.test(l11[c4 + 1]) && P6.test(l11[c4])) {
      l11 = l11.slice(c4);
      break;
    }
  }
  if (a2 != s99) {
    for (let c4 = l11.length - 1; c4 > l11.length - D5; c4--) if (!P6.test(l11[c4 - 1]) && P6.test(l11[c4])) {
      l11 = l11.slice(0, c4);
      break;
    }
  }
  return M2.announce.of(`${n22.state.phrase("current match")}. ${l11} ${n22.state.phrase("on line")} ${n22.state.doc.lineAt(e4).number}`);
}
var ze4 = M2.baseTheme({
  ".cm-panel.cm-search": {
    padding: "2px 6px 4px",
    position: "relative",
    "& [name=close]": {
      position: "absolute",
      top: "0",
      right: "4px",
      backgroundColor: "inherit",
      border: "none",
      font: "inherit",
      padding: 0,
      margin: 0
    },
    "& input, & button, & label": {
      margin: ".2em .6em .2em 0"
    },
    "& input[type=checkbox]": {
      marginRight: ".2em"
    },
    "& label": {
      fontSize: "80%",
      whiteSpace: "pre"
    }
  },
  "&light .cm-searchMatch": {
    backgroundColor: "#ffff0054"
  },
  "&dark .cm-searchMatch": {
    backgroundColor: "#00ffff8a"
  },
  "&light .cm-searchMatch-selected": {
    backgroundColor: "#ff6a0054"
  },
  "&dark .cm-searchMatch-selected": {
    backgroundColor: "#ff00ff8a"
  }
});
var G5 = [
  p3,
  lt.lowest(Ee4),
  ze4
];

// deno:https://esm.sh/@codemirror/basic-setup@0.20.0/denonext/basic-setup.mjs
var I7 = [
  go(),
  bo(),
  to(),
  un(),
  tn2(),
  Zr(),
  Qr(),
  I.allowMultipleSelections.of(true),
  Xe3(),
  en2(rn2, {
    fallback: true
  }),
  sn2(),
  zt(),
  Xt2(),
  no(),
  ro(),
  io(),
  Te6(),
  ur.of([
    ...Qt2,
    ...Tn2,
    ...Be5,
    ...dn,
    ..._e4,
    ...jt3,
    ...pe5
  ])
];

// deno:https://esm.sh/@marijn/find-cluster-break@1.0.2/denonext/find-cluster-break.mjs
var l9 = [];
var o3 = [];
(() => {
  let t5 = "lc,34,7n,7,7b,19,,,,2,,2,,,20,b,1c,l,g,,2t,7,2,6,2,2,,4,z,,u,r,2j,b,1m,9,9,,o,4,,9,,3,,5,17,3,3b,f,,w,1j,,,,4,8,4,,3,7,a,2,t,,1m,,,,2,4,8,,9,,a,2,q,,2,2,1l,,4,2,4,2,2,3,3,,u,2,3,,b,2,1l,,4,5,,2,4,,k,2,m,6,,,1m,,,2,,4,8,,7,3,a,2,u,,1n,,,,c,,9,,14,,3,,1l,3,5,3,,4,7,2,b,2,t,,1m,,2,,2,,3,,5,2,7,2,b,2,s,2,1l,2,,,2,4,8,,9,,a,2,t,,20,,4,,2,3,,,8,,29,,2,7,c,8,2q,,2,9,b,6,22,2,r,,,,,,1j,e,,5,,2,5,b,,10,9,,2u,4,,6,,2,2,2,p,2,4,3,g,4,d,,2,2,6,,f,,jj,3,qa,3,t,3,t,2,u,2,1s,2,,7,8,,2,b,9,,19,3,3b,2,y,,3a,3,4,2,9,,6,3,63,2,2,,1m,,,7,,,,,2,8,6,a,2,,1c,h,1r,4,1c,7,,,5,,14,9,c,2,w,4,2,2,,3,1k,,,2,3,,,3,1m,8,2,2,48,3,,d,,7,4,,6,,3,2,5i,1m,,5,ek,,5f,x,2da,3,3x,,2o,w,fe,6,2x,2,n9w,4,,a,w,2,28,2,7k,,3,,4,,p,2,5,,47,2,q,i,d,,12,8,p,b,1a,3,1c,,2,4,2,2,13,,1v,6,2,2,2,2,c,,8,,1b,,1f,,,3,2,2,5,2,,,16,2,8,,6m,,2,,4,,fn4,,kh,g,g,g,a6,2,gt,,6a,,45,5,1ae,3,,2,5,4,14,3,4,,4l,2,fx,4,ar,2,49,b,4w,,1i,f,1k,3,1d,4,2,2,1x,3,10,5,,8,1q,,c,2,1g,9,a,4,2,,2n,3,2,,,2,6,,4g,,3,8,l,2,1l,2,,,,,m,,e,7,3,5,5f,8,2,3,,,n,,29,,2,6,,,2,,,2,,2,6j,,2,4,6,2,,2,r,2,2d,8,2,,,2,2y,,,,2,6,,,2t,3,2,4,,5,77,9,,2,6t,,a,2,,,4,,40,4,2,2,4,,w,a,14,6,2,4,8,,9,6,2,3,1a,d,,2,ba,7,,6,,,2a,m,2,7,,2,,2,3e,6,3,,,2,,7,,,20,2,3,,,,9n,2,f0b,5,1n,7,t4,,1r,4,29,,f5k,2,43q,,,3,4,5,8,8,2,7,u,4,44,3,1iz,1j,4,1e,8,,e,,m,5,,f,11s,7,,h,2,7,,2,,5,79,7,c5,4,15s,7,31,7,240,5,gx7k,2o,3k,6o".split(",").map((e4) => e4 ? parseInt(e4, 36) : 1);
  for (let e4 = 0, n22 = 0; e4 < t5.length; e4++) (e4 % 2 ? o3 : l9).push(n22 = n22 + t5[e4]);
})();
function m6(t5) {
  if (t5 < 768) return false;
  for (let e4 = 0, n22 = l9.length; ; ) {
    let r2 = e4 + n22 >> 1;
    if (t5 < l9[r2]) n22 = r2;
    else if (t5 >= o3[r2]) e4 = r2 + 1;
    else return true;
    if (e4 == n22) return false;
  }
}
function c3(t5) {
  return t5 >= 127462 && t5 <= 127487;
}
var g4 = 8205;
function w7(t5, e4, n22 = true, r2 = true) {
  return (n22 ? b6 : k6)(t5, e4, r2);
}
function b6(t5, e4, n22) {
  if (e4 == t5.length) return e4;
  e4 && d2(t5.charCodeAt(e4)) && h2(t5.charCodeAt(e4 - 1)) && e4--;
  let r2 = u3(t5, e4);
  for (e4 += x7(r2); e4 < t5.length; ) {
    let f2 = u3(t5, e4);
    if (r2 == g4 || f2 == g4 || n22 && m6(f2)) e4 += x7(f2), r2 = f2;
    else if (c3(f2)) {
      let a2 = 0, i9 = e4 - 2;
      for (; i9 >= 0 && c3(u3(t5, i9)); ) a2++, i9 -= 2;
      if (a2 % 2 == 0) break;
      e4 += 2;
    } else break;
  }
  return e4;
}
function k6(t5, e4, n22) {
  for (; e4 > 0; ) {
    let r2 = b6(t5, e4 - 2, n22);
    if (r2 < e4) return r2;
    e4--;
  }
  return 0;
}
function u3(t5, e4) {
  let n22 = t5.charCodeAt(e4);
  if (!h2(n22) || e4 + 1 == t5.length) return n22;
  let r2 = t5.charCodeAt(e4 + 1);
  return d2(r2) ? (n22 - 55296 << 10) + (r2 - 56320) + 65536 : n22;
}
function d2(t5) {
  return t5 >= 56320 && t5 < 57344;
}
function h2(t5) {
  return t5 >= 55296 && t5 < 56320;
}
function x7(t5) {
  return t5 < 65536 ? 1 : 2;
}

// deno:https://esm.sh/@codemirror/state@6.5.3/denonext/state.mjs
var m7 = class s46 {
  lineAt(e4) {
    if (e4 < 0 || e4 > this.length) throw new RangeError(`Invalid position ${e4} in document of length ${this.length}`);
    return this.lineInner(e4, false, 1, 0);
  }
  line(e4) {
    if (e4 < 1 || e4 > this.lines) throw new RangeError(`Invalid line number ${e4} in ${this.lines}-line document`);
    return this.lineInner(e4, true, 1, 0);
  }
  replace(e4, t5, n22) {
    [e4, t5] = $6(this, e4, t5);
    let i9 = [];
    return this.decompose(0, e4, i9, 2), n22.length && n22.decompose(0, n22.length, i9, 3), this.decompose(t5, this.length, i9, 1), J6.from(i9, this.length - (t5 - e4) + n22.length);
  }
  append(e4) {
    return this.replace(this.length, this.length, e4);
  }
  slice(e4, t5 = this.length) {
    [e4, t5] = $6(this, e4, t5);
    let n22 = [];
    return this.decompose(e4, t5, n22, 0), J6.from(n22, t5 - e4);
  }
  eq(e4) {
    if (e4 == this) return true;
    if (e4.length != this.length || e4.lines != this.lines) return false;
    let t5 = this.scanIdentical(e4, 1), n22 = this.length - this.scanIdentical(e4, -1), i9 = new B8(this), r2 = new B8(e4);
    for (let l11 = t5, h3 = t5; ; ) {
      if (i9.next(l11), r2.next(l11), l11 = 0, i9.lineBreak != r2.lineBreak || i9.done != r2.done || i9.value != r2.value) return false;
      if (h3 += i9.value.length, i9.done || h3 >= n22) return true;
    }
  }
  iter(e4 = 1) {
    return new B8(this, e4);
  }
  iterRange(e4, t5 = this.length) {
    return new j7(this, e4, t5);
  }
  iterLines(e4, t5) {
    let n22;
    if (e4 == null) n22 = this.iter();
    else {
      t5 == null && (t5 = this.lines + 1);
      let i9 = this.line(e4).from;
      n22 = this.iterRange(i9, Math.max(i9, t5 == this.lines + 1 ? this.length : t5 <= 1 ? 0 : this.line(t5 - 1).to));
    }
    return new _7(n22);
  }
  toString() {
    return this.sliceString(0);
  }
  toJSON() {
    let e4 = [];
    return this.flatten(e4), e4;
  }
  constructor() {
  }
  static of(e4) {
    if (e4.length == 0) throw new RangeError("A document must have at least one line");
    return e4.length == 1 && !e4[0] ? s46.empty : e4.length <= 32 ? new y7(e4) : J6.from(y7.split(e4, []));
  }
};
var y7 = class s47 extends m7 {
  constructor(e4, t5 = ze5(e4)) {
    super(), this.text = e4, this.length = t5;
  }
  get lines() {
    return this.text.length;
  }
  get children() {
    return null;
  }
  lineInner(e4, t5, n22, i9) {
    for (let r2 = 0; ; r2++) {
      let l11 = this.text[r2], h3 = i9 + l11.length;
      if ((t5 ? n22 : h3) >= e4) return new ae8(i9, h3, n22, l11);
      i9 = h3 + 1, n22++;
    }
  }
  decompose(e4, t5, n22, i9) {
    let r2 = e4 <= 0 && t5 >= this.length ? this : new s47(Ae5(this.text, e4, t5), Math.min(t5, this.length) - Math.max(0, e4));
    if (i9 & 1) {
      let l11 = n22.pop(), h3 = Z9(r2.text, l11.text.slice(), 0, r2.length);
      if (h3.length <= 32) n22.push(new s47(h3, l11.length + r2.length));
      else {
        let o4 = h3.length >> 1;
        n22.push(new s47(h3.slice(0, o4)), new s47(h3.slice(o4)));
      }
    } else n22.push(r2);
  }
  replace(e4, t5, n22) {
    if (!(n22 instanceof s47)) return super.replace(e4, t5, n22);
    [e4, t5] = $6(this, e4, t5);
    let i9 = Z9(this.text, Z9(n22.text, Ae5(this.text, 0, e4)), t5), r2 = this.length + n22.length - (t5 - e4);
    return i9.length <= 32 ? new s47(i9, r2) : J6.from(s47.split(i9, []), r2);
  }
  sliceString(e4, t5 = this.length, n22 = `
`) {
    [e4, t5] = $6(this, e4, t5);
    let i9 = "";
    for (let r2 = 0, l11 = 0; r2 <= t5 && l11 < this.text.length; l11++) {
      let h3 = this.text[l11], o4 = r2 + h3.length;
      r2 > e4 && l11 && (i9 += n22), e4 < o4 && t5 > r2 && (i9 += h3.slice(Math.max(0, e4 - r2), t5 - r2)), r2 = o4 + 1;
    }
    return i9;
  }
  flatten(e4) {
    for (let t5 of this.text) e4.push(t5);
  }
  scanIdentical() {
    return 0;
  }
  static split(e4, t5) {
    let n22 = [], i9 = -1;
    for (let r2 of e4) n22.push(r2), i9 += r2.length + 1, n22.length == 32 && (t5.push(new s47(n22, i9)), n22 = [], i9 = -1);
    return i9 > -1 && t5.push(new s47(n22, i9)), t5;
  }
};
var J6 = class s48 extends m7 {
  constructor(e4, t5) {
    super(), this.children = e4, this.length = t5, this.lines = 0;
    for (let n22 of e4) this.lines += n22.lines;
  }
  lineInner(e4, t5, n22, i9) {
    for (let r2 = 0; ; r2++) {
      let l11 = this.children[r2], h3 = i9 + l11.length, o4 = n22 + l11.lines - 1;
      if ((t5 ? o4 : h3) >= e4) return l11.lineInner(e4, t5, n22, i9);
      i9 = h3 + 1, n22 = o4 + 1;
    }
  }
  decompose(e4, t5, n22, i9) {
    for (let r2 = 0, l11 = 0; l11 <= t5 && r2 < this.children.length; r2++) {
      let h3 = this.children[r2], o4 = l11 + h3.length;
      if (e4 <= o4 && t5 >= l11) {
        let a2 = i9 & ((l11 <= e4 ? 1 : 0) | (o4 >= t5 ? 2 : 0));
        l11 >= e4 && o4 <= t5 && !a2 ? n22.push(h3) : h3.decompose(e4 - l11, t5 - l11, n22, a2);
      }
      l11 = o4 + 1;
    }
  }
  replace(e4, t5, n22) {
    if ([e4, t5] = $6(this, e4, t5), n22.lines < this.lines) for (let i9 = 0, r2 = 0; i9 < this.children.length; i9++) {
      let l11 = this.children[i9], h3 = r2 + l11.length;
      if (e4 >= r2 && t5 <= h3) {
        let o4 = l11.replace(e4 - r2, t5 - r2, n22), a2 = this.lines - l11.lines + o4.lines;
        if (o4.lines < a2 >> 4 && o4.lines > a2 >> 6) {
          let f2 = this.children.slice();
          return f2[i9] = o4, new s48(f2, this.length - (t5 - e4) + n22.length);
        }
        return super.replace(r2, h3, o4);
      }
      r2 = h3 + 1;
    }
    return super.replace(e4, t5, n22);
  }
  sliceString(e4, t5 = this.length, n22 = `
`) {
    [e4, t5] = $6(this, e4, t5);
    let i9 = "";
    for (let r2 = 0, l11 = 0; r2 < this.children.length && l11 <= t5; r2++) {
      let h3 = this.children[r2], o4 = l11 + h3.length;
      l11 > e4 && r2 && (i9 += n22), e4 < o4 && t5 > l11 && (i9 += h3.sliceString(e4 - l11, t5 - l11, n22)), l11 = o4 + 1;
    }
    return i9;
  }
  flatten(e4) {
    for (let t5 of this.children) t5.flatten(e4);
  }
  scanIdentical(e4, t5) {
    if (!(e4 instanceof s48)) return 0;
    let n22 = 0, [i9, r2, l11, h3] = t5 > 0 ? [
      0,
      0,
      this.children.length,
      e4.children.length
    ] : [
      this.children.length - 1,
      e4.children.length - 1,
      -1,
      -1
    ];
    for (; ; i9 += t5, r2 += t5) {
      if (i9 == l11 || r2 == h3) return n22;
      let o4 = this.children[i9], a2 = e4.children[r2];
      if (o4 != a2) return n22 + o4.scanIdentical(a2, t5);
      n22 += o4.length + 1;
    }
  }
  static from(e4, t5 = e4.reduce((n22, i9) => n22 + i9.length + 1, -1)) {
    let n22 = 0;
    for (let c4 of e4) n22 += c4.lines;
    if (n22 < 32) {
      let c4 = [];
      for (let g6 of e4) g6.flatten(c4);
      return new y7(c4, t5);
    }
    let i9 = Math.max(32, n22 >> 5), r2 = i9 << 1, l11 = i9 >> 1, h3 = [], o4 = 0, a2 = -1, f2 = [];
    function u5(c4) {
      let g6;
      if (c4.lines > r2 && c4 instanceof s48) for (let I13 of c4.children) u5(I13);
      else c4.lines > l11 && (o4 > l11 || !o4) ? (d5(), h3.push(c4)) : c4 instanceof y7 && o4 && (g6 = f2[f2.length - 1]) instanceof y7 && c4.lines + g6.lines <= 32 ? (o4 += c4.lines, a2 += c4.length + 1, f2[f2.length - 1] = new y7(g6.text.concat(c4.text), g6.length + 1 + c4.length)) : (o4 + c4.lines > i9 && d5(), o4 += c4.lines, a2 += c4.length + 1, f2.push(c4));
    }
    function d5() {
      o4 != 0 && (h3.push(f2.length == 1 ? f2[0] : s48.from(f2, a2)), a2 = -1, o4 = f2.length = 0);
    }
    for (let c4 of e4) u5(c4);
    return d5(), h3.length == 1 ? h3[0] : new s48(h3, t5);
  }
};
m7.empty = new y7([
  ""
], 0);
function ze5(s99) {
  let e4 = -1;
  for (let t5 of s99) e4 += t5.length + 1;
  return e4;
}
function Z9(s99, e4, t5 = 0, n22 = 1e9) {
  for (let i9 = 0, r2 = 0, l11 = true; r2 < s99.length && i9 <= n22; r2++) {
    let h3 = s99[r2], o4 = i9 + h3.length;
    o4 >= t5 && (o4 > n22 && (h3 = h3.slice(0, n22 - i9)), i9 < t5 && (h3 = h3.slice(t5 - i9)), l11 ? (e4[e4.length - 1] += h3, l11 = false) : e4.push(h3)), i9 = o4 + 1;
  }
  return e4;
}
function Ae5(s99, e4, t5) {
  return Z9(s99, [
    ""
  ], e4, t5);
}
var B8 = class {
  constructor(e4, t5 = 1) {
    this.dir = t5, this.done = false, this.lineBreak = false, this.value = "", this.nodes = [
      e4
    ], this.offsets = [
      t5 > 0 ? 1 : (e4 instanceof y7 ? e4.text.length : e4.children.length) << 1
    ];
  }
  nextInner(e4, t5) {
    for (this.done = this.lineBreak = false; ; ) {
      let n22 = this.nodes.length - 1, i9 = this.nodes[n22], r2 = this.offsets[n22], l11 = r2 >> 1, h3 = i9 instanceof y7 ? i9.text.length : i9.children.length;
      if (l11 == (t5 > 0 ? h3 : 0)) {
        if (n22 == 0) return this.done = true, this.value = "", this;
        t5 > 0 && this.offsets[n22 - 1]++, this.nodes.pop(), this.offsets.pop();
      } else if ((r2 & 1) == (t5 > 0 ? 0 : 1)) {
        if (this.offsets[n22] += t5, e4 == 0) return this.lineBreak = true, this.value = `
`, this;
        e4--;
      } else if (i9 instanceof y7) {
        let o4 = i9.text[l11 + (t5 < 0 ? -1 : 0)];
        if (this.offsets[n22] += t5, o4.length > Math.max(0, e4)) return this.value = e4 == 0 ? o4 : t5 > 0 ? o4.slice(e4) : o4.slice(0, o4.length - e4), this;
        e4 -= o4.length;
      } else {
        let o4 = i9.children[l11 + (t5 < 0 ? -1 : 0)];
        e4 > o4.length ? (e4 -= o4.length, this.offsets[n22] += t5) : (t5 < 0 && this.offsets[n22]--, this.nodes.push(o4), this.offsets.push(t5 > 0 ? 1 : (o4 instanceof y7 ? o4.text.length : o4.children.length) << 1));
      }
    }
  }
  next(e4 = 0) {
    return e4 < 0 && (this.nextInner(-e4, -this.dir), e4 = this.value.length), this.nextInner(e4, this.dir);
  }
};
var j7 = class {
  constructor(e4, t5, n22) {
    this.value = "", this.done = false, this.cursor = new B8(e4, t5 > n22 ? -1 : 1), this.pos = t5 > n22 ? e4.length : 0, this.from = Math.min(t5, n22), this.to = Math.max(t5, n22);
  }
  nextInner(e4, t5) {
    if (t5 < 0 ? this.pos <= this.from : this.pos >= this.to) return this.value = "", this.done = true, this;
    e4 += Math.max(0, t5 < 0 ? this.pos - this.to : this.from - this.pos);
    let n22 = t5 < 0 ? this.pos - this.from : this.to - this.pos;
    e4 > n22 && (e4 = n22), n22 -= e4;
    let { value: i9 } = this.cursor.next(e4);
    return this.pos += (i9.length + e4) * t5, this.value = i9.length <= n22 ? i9 : t5 < 0 ? i9.slice(i9.length - n22) : i9.slice(0, n22), this.done = !this.value, this;
  }
  next(e4 = 0) {
    return e4 < 0 ? e4 = Math.max(e4, this.from - this.pos) : e4 > 0 && (e4 = Math.min(e4, this.to - this.pos)), this.nextInner(e4, this.cursor.dir);
  }
  get lineBreak() {
    return this.cursor.lineBreak && this.value != "";
  }
};
var _7 = class {
  constructor(e4) {
    this.inner = e4, this.afterBreak = true, this.value = "", this.done = false;
  }
  next(e4 = 0) {
    let { done: t5, lineBreak: n22, value: i9 } = this.inner.next(e4);
    return t5 && this.afterBreak ? (this.value = "", this.afterBreak = false) : t5 ? (this.done = true, this.value = "") : n22 ? this.afterBreak ? this.value = "" : (this.afterBreak = true, this.next()) : (this.value = i9, this.afterBreak = false), this;
  }
  get lineBreak() {
    return false;
  }
};
typeof Symbol < "u" && (m7.prototype[Symbol.iterator] = function() {
  return this.iter();
}, B8.prototype[Symbol.iterator] = j7.prototype[Symbol.iterator] = _7.prototype[Symbol.iterator] = function() {
  return this;
});
var ae8 = class {
  constructor(e4, t5, n22, i9) {
    this.from = e4, this.to = t5, this.number = n22, this.text = i9;
  }
  get length() {
    return this.to - this.from;
  }
};
function $6(s99, e4, t5) {
  return e4 = Math.max(0, Math.min(s99.length, e4)), [
    e4,
    Math.max(e4, Math.min(s99.length, t5))
  ];
}
function ee6(s99, e4, t5 = true, n22 = true) {
  return w7(s99, e4, t5, n22);
}
function qe5(s99) {
  return s99 >= 56320 && s99 < 57344;
}
function We5(s99) {
  return s99 >= 55296 && s99 < 56320;
}
function tt5(s99, e4) {
  let t5 = s99.charCodeAt(e4);
  if (!We5(t5) || e4 + 1 == s99.length) return t5;
  let n22 = s99.charCodeAt(e4 + 1);
  return qe5(n22) ? (t5 - 55296 << 10) + (n22 - 56320) + 65536 : t5;
}
function nt3(s99) {
  return s99 <= 65535 ? String.fromCharCode(s99) : (s99 -= 65536, String.fromCharCode((s99 >> 10) + 55296, (s99 & 1023) + 56320));
}
function it5(s99) {
  return s99 < 65536 ? 1 : 2;
}
var fe6 = /\r\n?|\n/;
var E6 = function(s99) {
  return s99[s99.Simple = 0] = "Simple", s99[s99.TrackDel = 1] = "TrackDel", s99[s99.TrackBefore = 2] = "TrackBefore", s99[s99.TrackAfter = 3] = "TrackAfter", s99;
}(E6 || (E6 = {}));
var C8 = class s49 {
  constructor(e4) {
    this.sections = e4;
  }
  get length() {
    let e4 = 0;
    for (let t5 = 0; t5 < this.sections.length; t5 += 2) e4 += this.sections[t5];
    return e4;
  }
  get newLength() {
    let e4 = 0;
    for (let t5 = 0; t5 < this.sections.length; t5 += 2) {
      let n22 = this.sections[t5 + 1];
      e4 += n22 < 0 ? this.sections[t5] : n22;
    }
    return e4;
  }
  get empty() {
    return this.sections.length == 0 || this.sections.length == 2 && this.sections[1] < 0;
  }
  iterGaps(e4) {
    for (let t5 = 0, n22 = 0, i9 = 0; t5 < this.sections.length; ) {
      let r2 = this.sections[t5++], l11 = this.sections[t5++];
      l11 < 0 ? (e4(n22, i9, r2), i9 += r2) : i9 += l11, n22 += r2;
    }
  }
  iterChangedRanges(e4, t5 = false) {
    ue7(this, e4, t5);
  }
  get invertedDesc() {
    let e4 = [];
    for (let t5 = 0; t5 < this.sections.length; ) {
      let n22 = this.sections[t5++], i9 = this.sections[t5++];
      i9 < 0 ? e4.push(n22, i9) : e4.push(i9, n22);
    }
    return new s49(e4);
  }
  composeDesc(e4) {
    return this.empty ? e4 : e4.empty ? this : be6(this, e4);
  }
  mapDesc(e4, t5 = false) {
    return e4.empty ? this : ce9(this, e4, t5);
  }
  mapPos(e4, t5 = -1, n22 = E6.Simple) {
    let i9 = 0, r2 = 0;
    for (let l11 = 0; l11 < this.sections.length; ) {
      let h3 = this.sections[l11++], o4 = this.sections[l11++], a2 = i9 + h3;
      if (o4 < 0) {
        if (a2 > e4) return r2 + (e4 - i9);
        r2 += h3;
      } else {
        if (n22 != E6.Simple && a2 >= e4 && (n22 == E6.TrackDel && i9 < e4 && a2 > e4 || n22 == E6.TrackBefore && i9 < e4 || n22 == E6.TrackAfter && a2 > e4)) return null;
        if (a2 > e4 || a2 == e4 && t5 < 0 && !h3) return e4 == i9 || t5 < 0 ? r2 : r2 + o4;
        r2 += o4;
      }
      i9 = a2;
    }
    if (e4 > i9) throw new RangeError(`Position ${e4} is out of range for changeset of length ${i9}`);
    return r2;
  }
  touchesRange(e4, t5 = e4) {
    for (let n22 = 0, i9 = 0; n22 < this.sections.length && i9 <= t5; ) {
      let r2 = this.sections[n22++], l11 = this.sections[n22++], h3 = i9 + r2;
      if (l11 >= 0 && i9 <= t5 && h3 >= e4) return i9 < e4 && h3 > t5 ? "cover" : true;
      i9 = h3;
    }
    return false;
  }
  toString() {
    let e4 = "";
    for (let t5 = 0; t5 < this.sections.length; ) {
      let n22 = this.sections[t5++], i9 = this.sections[t5++];
      e4 += (e4 ? " " : "") + n22 + (i9 >= 0 ? ":" + i9 : "");
    }
    return e4;
  }
  toJSON() {
    return this.sections;
  }
  static fromJSON(e4) {
    if (!Array.isArray(e4) || e4.length % 2 || e4.some((t5) => typeof t5 != "number")) throw new RangeError("Invalid JSON representation of ChangeDesc");
    return new s49(e4);
  }
  static create(e4) {
    return new s49(e4);
  }
};
var A8 = class s50 extends C8 {
  constructor(e4, t5) {
    super(e4), this.inserted = t5;
  }
  apply(e4) {
    if (this.length != e4.length) throw new RangeError("Applying change set to a document with the wrong length");
    return ue7(this, (t5, n22, i9, r2, l11) => e4 = e4.replace(i9, i9 + (n22 - t5), l11), false), e4;
  }
  mapDesc(e4, t5 = false) {
    return ce9(this, e4, t5, true);
  }
  invert(e4) {
    let t5 = this.sections.slice(), n22 = [];
    for (let i9 = 0, r2 = 0; i9 < t5.length; i9 += 2) {
      let l11 = t5[i9], h3 = t5[i9 + 1];
      if (h3 >= 0) {
        t5[i9] = h3, t5[i9 + 1] = l11;
        let o4 = i9 >> 1;
        for (; n22.length < o4; ) n22.push(m7.empty);
        n22.push(l11 ? e4.slice(r2, r2 + l11) : m7.empty);
      }
      r2 += l11;
    }
    return new s50(t5, n22);
  }
  compose(e4) {
    return this.empty ? e4 : e4.empty ? this : be6(this, e4, true);
  }
  map(e4, t5 = false) {
    return e4.empty ? this : ce9(this, e4, t5, true);
  }
  iterChanges(e4, t5 = false) {
    ue7(this, e4, t5);
  }
  get desc() {
    return C8.create(this.sections);
  }
  filter(e4) {
    let t5 = [], n22 = [], i9 = [], r2 = new F7(this);
    e: for (let l11 = 0, h3 = 0; ; ) {
      let o4 = l11 == e4.length ? 1e9 : e4[l11++];
      for (; h3 < o4 || h3 == o4 && r2.len == 0; ) {
        if (r2.done) break e;
        let f2 = Math.min(r2.len, o4 - h3);
        w8(i9, f2, -1);
        let u5 = r2.ins == -1 ? -1 : r2.off == 0 ? r2.ins : 0;
        w8(t5, f2, u5), u5 > 0 && O6(n22, t5, r2.text), r2.forward(f2), h3 += f2;
      }
      let a2 = e4[l11++];
      for (; h3 < a2; ) {
        if (r2.done) break e;
        let f2 = Math.min(r2.len, a2 - h3);
        w8(t5, f2, -1), w8(i9, f2, r2.ins == -1 ? -1 : r2.off == 0 ? r2.ins : 0), r2.forward(f2), h3 += f2;
      }
    }
    return {
      changes: new s50(t5, n22),
      filtered: C8.create(i9)
    };
  }
  toJSON() {
    let e4 = [];
    for (let t5 = 0; t5 < this.sections.length; t5 += 2) {
      let n22 = this.sections[t5], i9 = this.sections[t5 + 1];
      i9 < 0 ? e4.push(n22) : i9 == 0 ? e4.push([
        n22
      ]) : e4.push([
        n22
      ].concat(this.inserted[t5 >> 1].toJSON()));
    }
    return e4;
  }
  static of(e4, t5, n22) {
    let i9 = [], r2 = [], l11 = 0, h3 = null;
    function o4(f2 = false) {
      if (!f2 && !i9.length) return;
      l11 < t5 && w8(i9, t5 - l11, -1);
      let u5 = new s50(i9, r2);
      h3 = h3 ? h3.compose(u5.map(h3)) : u5, i9 = [], r2 = [], l11 = 0;
    }
    function a2(f2) {
      if (Array.isArray(f2)) for (let u5 of f2) a2(u5);
      else if (f2 instanceof s50) {
        if (f2.length != t5) throw new RangeError(`Mismatched change set length (got ${f2.length}, expected ${t5})`);
        o4(), h3 = h3 ? h3.compose(f2.map(h3)) : f2;
      } else {
        let { from: u5, to: d5 = u5, insert: c4 } = f2;
        if (u5 > d5 || u5 < 0 || d5 > t5) throw new RangeError(`Invalid change range ${u5} to ${d5} (in doc of length ${t5})`);
        let g6 = c4 ? typeof c4 == "string" ? m7.of(c4.split(n22 || fe6)) : c4 : m7.empty, I13 = g6.length;
        if (u5 == d5 && I13 == 0) return;
        u5 < l11 && o4(), u5 > l11 && w8(i9, u5 - l11, -1), w8(i9, d5 - u5, I13), O6(r2, i9, g6), l11 = d5;
      }
    }
    return a2(e4), o4(!h3), h3;
  }
  static empty(e4) {
    return new s50(e4 ? [
      e4,
      -1
    ] : [], []);
  }
  static fromJSON(e4) {
    if (!Array.isArray(e4)) throw new RangeError("Invalid JSON representation of ChangeSet");
    let t5 = [], n22 = [];
    for (let i9 = 0; i9 < e4.length; i9++) {
      let r2 = e4[i9];
      if (typeof r2 == "number") t5.push(r2, -1);
      else {
        if (!Array.isArray(r2) || typeof r2[0] != "number" || r2.some((l11, h3) => h3 && typeof l11 != "string")) throw new RangeError("Invalid JSON representation of ChangeSet");
        if (r2.length == 1) t5.push(r2[0], 0);
        else {
          for (; n22.length < i9; ) n22.push(m7.empty);
          n22[i9] = m7.of(r2.slice(1)), t5.push(r2[0], n22[i9].length);
        }
      }
    }
    return new s50(t5, n22);
  }
  static createSet(e4, t5) {
    return new s50(e4, t5);
  }
};
function w8(s99, e4, t5, n22 = false) {
  if (e4 == 0 && t5 <= 0) return;
  let i9 = s99.length - 2;
  i9 >= 0 && t5 <= 0 && t5 == s99[i9 + 1] ? s99[i9] += e4 : i9 >= 0 && e4 == 0 && s99[i9] == 0 ? s99[i9 + 1] += t5 : n22 ? (s99[i9] += e4, s99[i9 + 1] += t5) : s99.push(e4, t5);
}
function O6(s99, e4, t5) {
  if (t5.length == 0) return;
  let n22 = e4.length - 2 >> 1;
  if (n22 < s99.length) s99[s99.length - 1] = s99[s99.length - 1].append(t5);
  else {
    for (; s99.length < n22; ) s99.push(m7.empty);
    s99.push(t5);
  }
}
function ue7(s99, e4, t5) {
  let n22 = s99.inserted;
  for (let i9 = 0, r2 = 0, l11 = 0; l11 < s99.sections.length; ) {
    let h3 = s99.sections[l11++], o4 = s99.sections[l11++];
    if (o4 < 0) i9 += h3, r2 += h3;
    else {
      let a2 = i9, f2 = r2, u5 = m7.empty;
      for (; a2 += h3, f2 += o4, o4 && n22 && (u5 = u5.append(n22[l11 - 2 >> 1])), !(t5 || l11 == s99.sections.length || s99.sections[l11 + 1] < 0); ) h3 = s99.sections[l11++], o4 = s99.sections[l11++];
      e4(i9, a2, r2, f2, u5), i9 = a2, r2 = f2;
    }
  }
}
function ce9(s99, e4, t5, n22 = false) {
  let i9 = [], r2 = n22 ? [] : null, l11 = new F7(s99), h3 = new F7(e4);
  for (let o4 = -1; ; ) {
    if (l11.done && h3.len || h3.done && l11.len) throw new Error("Mismatched change set lengths");
    if (l11.ins == -1 && h3.ins == -1) {
      let a2 = Math.min(l11.len, h3.len);
      w8(i9, a2, -1), l11.forward(a2), h3.forward(a2);
    } else if (h3.ins >= 0 && (l11.ins < 0 || o4 == l11.i || l11.off == 0 && (h3.len < l11.len || h3.len == l11.len && !t5))) {
      let a2 = h3.len;
      for (w8(i9, h3.ins, -1); a2; ) {
        let f2 = Math.min(l11.len, a2);
        l11.ins >= 0 && o4 < l11.i && l11.len <= f2 && (w8(i9, 0, l11.ins), r2 && O6(r2, i9, l11.text), o4 = l11.i), l11.forward(f2), a2 -= f2;
      }
      h3.next();
    } else if (l11.ins >= 0) {
      let a2 = 0, f2 = l11.len;
      for (; f2; ) if (h3.ins == -1) {
        let u5 = Math.min(f2, h3.len);
        a2 += u5, f2 -= u5, h3.forward(u5);
      } else if (h3.ins == 0 && h3.len < f2) f2 -= h3.len, h3.next();
      else break;
      w8(i9, a2, o4 < l11.i ? l11.ins : 0), r2 && o4 < l11.i && O6(r2, i9, l11.text), o4 = l11.i, l11.forward(l11.len - f2);
    } else {
      if (l11.done && h3.done) return r2 ? A8.createSet(i9, r2) : C8.create(i9);
      throw new Error("Mismatched change set lengths");
    }
  }
}
function be6(s99, e4, t5 = false) {
  let n22 = [], i9 = t5 ? [] : null, r2 = new F7(s99), l11 = new F7(e4);
  for (let h3 = false; ; ) {
    if (r2.done && l11.done) return i9 ? A8.createSet(n22, i9) : C8.create(n22);
    if (r2.ins == 0) w8(n22, r2.len, 0, h3), r2.next();
    else if (l11.len == 0 && !l11.done) w8(n22, 0, l11.ins, h3), i9 && O6(i9, n22, l11.text), l11.next();
    else {
      if (r2.done || l11.done) throw new Error("Mismatched change set lengths");
      {
        let o4 = Math.min(r2.len2, l11.len), a2 = n22.length;
        if (r2.ins == -1) {
          let f2 = l11.ins == -1 ? -1 : l11.off ? 0 : l11.ins;
          w8(n22, o4, f2, h3), i9 && f2 && O6(i9, n22, l11.text);
        } else l11.ins == -1 ? (w8(n22, r2.off ? 0 : r2.len, o4, h3), i9 && O6(i9, n22, r2.textBit(o4))) : (w8(n22, r2.off ? 0 : r2.len, l11.off ? 0 : l11.ins, h3), i9 && !l11.off && O6(i9, n22, l11.text));
        h3 = (r2.ins > o4 || l11.ins >= 0 && l11.len > o4) && (h3 || n22.length > a2), r2.forward2(o4), l11.forward(o4);
      }
    }
  }
}
var F7 = class {
  constructor(e4) {
    this.set = e4, this.i = 0, this.next();
  }
  next() {
    let { sections: e4 } = this.set;
    this.i < e4.length ? (this.len = e4[this.i++], this.ins = e4[this.i++]) : (this.len = 0, this.ins = -2), this.off = 0;
  }
  get done() {
    return this.ins == -2;
  }
  get len2() {
    return this.ins < 0 ? this.len : this.ins;
  }
  get text() {
    let { inserted: e4 } = this.set, t5 = this.i - 2 >> 1;
    return t5 >= e4.length ? m7.empty : e4[t5];
  }
  textBit(e4) {
    let { inserted: t5 } = this.set, n22 = this.i - 2 >> 1;
    return n22 >= t5.length && !e4 ? m7.empty : t5[n22].slice(this.off, e4 == null ? void 0 : this.off + e4);
  }
  forward(e4) {
    e4 == this.len ? this.next() : (this.len -= e4, this.off += e4);
  }
  forward2(e4) {
    this.ins == -1 ? this.forward(e4) : e4 == this.ins ? this.next() : (this.ins -= e4, this.off += e4);
  }
};
var N9 = class s51 {
  constructor(e4, t5, n22) {
    this.from = e4, this.to = t5, this.flags = n22;
  }
  get anchor() {
    return this.flags & 32 ? this.to : this.from;
  }
  get head() {
    return this.flags & 32 ? this.from : this.to;
  }
  get empty() {
    return this.from == this.to;
  }
  get assoc() {
    return this.flags & 8 ? -1 : this.flags & 16 ? 1 : 0;
  }
  get bidiLevel() {
    let e4 = this.flags & 7;
    return e4 == 7 ? null : e4;
  }
  get goalColumn() {
    let e4 = this.flags >> 6;
    return e4 == 16777215 ? void 0 : e4;
  }
  map(e4, t5 = -1) {
    let n22, i9;
    return this.empty ? n22 = i9 = e4.mapPos(this.from, t5) : (n22 = e4.mapPos(this.from, 1), i9 = e4.mapPos(this.to, -1)), n22 == this.from && i9 == this.to ? this : new s51(n22, i9, this.flags);
  }
  extend(e4, t5 = e4) {
    if (e4 <= this.anchor && t5 >= this.anchor) return x8.range(e4, t5);
    let n22 = Math.abs(e4 - this.anchor) > Math.abs(t5 - this.anchor) ? e4 : t5;
    return x8.range(this.anchor, n22);
  }
  eq(e4, t5 = false) {
    return this.anchor == e4.anchor && this.head == e4.head && (!t5 || !this.empty || this.assoc == e4.assoc);
  }
  toJSON() {
    return {
      anchor: this.anchor,
      head: this.head
    };
  }
  static fromJSON(e4) {
    if (!e4 || typeof e4.anchor != "number" || typeof e4.head != "number") throw new RangeError("Invalid JSON representation for SelectionRange");
    return x8.range(e4.anchor, e4.head);
  }
  static create(e4, t5, n22) {
    return new s51(e4, t5, n22);
  }
};
var x8 = class s52 {
  constructor(e4, t5) {
    this.ranges = e4, this.mainIndex = t5;
  }
  map(e4, t5 = -1) {
    return e4.empty ? this : s52.create(this.ranges.map((n22) => n22.map(e4, t5)), this.mainIndex);
  }
  eq(e4, t5 = false) {
    if (this.ranges.length != e4.ranges.length || this.mainIndex != e4.mainIndex) return false;
    for (let n22 = 0; n22 < this.ranges.length; n22++) if (!this.ranges[n22].eq(e4.ranges[n22], t5)) return false;
    return true;
  }
  get main() {
    return this.ranges[this.mainIndex];
  }
  asSingle() {
    return this.ranges.length == 1 ? this : new s52([
      this.main
    ], 0);
  }
  addRange(e4, t5 = true) {
    return s52.create([
      e4
    ].concat(this.ranges), t5 ? 0 : this.mainIndex + 1);
  }
  replaceRange(e4, t5 = this.mainIndex) {
    let n22 = this.ranges.slice();
    return n22[t5] = e4, s52.create(n22, this.mainIndex);
  }
  toJSON() {
    return {
      ranges: this.ranges.map((e4) => e4.toJSON()),
      main: this.mainIndex
    };
  }
  static fromJSON(e4) {
    if (!e4 || !Array.isArray(e4.ranges) || typeof e4.main != "number" || e4.main >= e4.ranges.length) throw new RangeError("Invalid JSON representation for EditorSelection");
    return new s52(e4.ranges.map((t5) => N9.fromJSON(t5)), e4.main);
  }
  static single(e4, t5 = e4) {
    return new s52([
      s52.range(e4, t5)
    ], 0);
  }
  static create(e4, t5 = 0) {
    if (e4.length == 0) throw new RangeError("A selection needs at least one range");
    for (let n22 = 0, i9 = 0; i9 < e4.length; i9++) {
      let r2 = e4[i9];
      if (r2.empty ? r2.from <= n22 : r2.from < n22) return s52.normalized(e4.slice(), t5);
      n22 = r2.to;
    }
    return new s52(e4, t5);
  }
  static cursor(e4, t5 = 0, n22, i9) {
    return N9.create(e4, e4, (t5 == 0 ? 0 : t5 < 0 ? 8 : 16) | (n22 == null ? 7 : Math.min(6, n22)) | (i9 ?? 16777215) << 6);
  }
  static range(e4, t5, n22, i9) {
    let r2 = (n22 ?? 16777215) << 6 | (i9 == null ? 7 : Math.min(6, i9));
    return t5 < e4 ? N9.create(t5, e4, 48 | r2) : N9.create(e4, t5, (t5 > e4 ? 8 : 0) | r2);
  }
  static normalized(e4, t5 = 0) {
    let n22 = e4[t5];
    e4.sort((i9, r2) => i9.from - r2.from), t5 = e4.indexOf(n22);
    for (let i9 = 1; i9 < e4.length; i9++) {
      let r2 = e4[i9], l11 = e4[i9 - 1];
      if (r2.empty ? r2.from <= l11.to : r2.from < l11.to) {
        let h3 = l11.from, o4 = Math.max(r2.to, l11.to);
        i9 <= t5 && t5--, e4.splice(--i9, 2, r2.anchor > r2.head ? s52.range(o4, h3) : s52.range(h3, o4));
      }
    }
    return new s52(e4, t5);
  }
};
function Re6(s99, e4) {
  for (let t5 of s99.ranges) if (t5.to > e4) throw new RangeError("Selection points outside of document");
}
var Se7 = 0;
var k7 = class s53 {
  constructor(e4, t5, n22, i9, r2) {
    this.combine = e4, this.compareInput = t5, this.compare = n22, this.isStatic = i9, this.id = Se7++, this.default = e4([]), this.extensions = typeof r2 == "function" ? r2(this) : r2;
  }
  get reader() {
    return this;
  }
  static define(e4 = {}) {
    return new s53(e4.combine || ((t5) => t5), e4.compareInput || ((t5, n22) => t5 === n22), e4.compare || (e4.combine ? (t5, n22) => t5 === n22 : Ie6), !!e4.static, e4.enables);
  }
  of(e4) {
    return new D6([], this, 0, e4);
  }
  compute(e4, t5) {
    if (this.isStatic) throw new Error("Can't compute a static facet");
    return new D6(e4, this, 1, t5);
  }
  computeN(e4, t5) {
    if (this.isStatic) throw new Error("Can't compute a static facet");
    return new D6(e4, this, 2, t5);
  }
  from(e4, t5) {
    return t5 || (t5 = (n22) => n22), this.compute([
      e4
    ], (n22) => t5(n22.field(e4)));
  }
};
function Ie6(s99, e4) {
  return s99 == e4 || s99.length == e4.length && s99.every((t5, n22) => t5 === e4[n22]);
}
var D6 = class {
  constructor(e4, t5, n22, i9) {
    this.dependencies = e4, this.facet = t5, this.type = n22, this.value = i9, this.id = Se7++;
  }
  dynamicSlot(e4) {
    var t5;
    let n22 = this.value, i9 = this.facet.compareInput, r2 = this.id, l11 = e4[r2] >> 1, h3 = this.type == 2, o4 = false, a2 = false, f2 = [];
    for (let u5 of this.dependencies) u5 == "doc" ? o4 = true : u5 == "selection" ? a2 = true : (((t5 = e4[u5.id]) !== null && t5 !== void 0 ? t5 : 1) & 1) == 0 && f2.push(e4[u5.id]);
    return {
      create(u5) {
        return u5.values[l11] = n22(u5), 1;
      },
      update(u5, d5) {
        if (o4 && d5.docChanged || a2 && (d5.docChanged || d5.selection) || de7(u5, f2)) {
          let c4 = n22(u5);
          if (h3 ? !Ee5(c4, u5.values[l11], i9) : !i9(c4, u5.values[l11])) return u5.values[l11] = c4, 1;
        }
        return 0;
      },
      reconfigure: (u5, d5) => {
        let c4, g6 = d5.config.address[r2];
        if (g6 != null) {
          let I13 = se8(d5, g6);
          if (this.dependencies.every((p5) => p5 instanceof k7 ? d5.facet(p5) === u5.facet(p5) : p5 instanceof z8 ? d5.field(p5, false) == u5.field(p5, false) : true) || (h3 ? Ee5(c4 = n22(u5), I13, i9) : i9(c4 = n22(u5), I13))) return u5.values[l11] = I13, 0;
        } else c4 = n22(u5);
        return u5.values[l11] = c4, 1;
      }
    };
  }
};
function Ee5(s99, e4, t5) {
  if (s99.length != e4.length) return false;
  for (let n22 = 0; n22 < s99.length; n22++) if (!t5(s99[n22], e4[n22])) return false;
  return true;
}
function de7(s99, e4) {
  let t5 = false;
  for (let n22 of e4) U8(s99, n22) & 1 && (t5 = true);
  return t5;
}
function Ue5(s99, e4, t5) {
  let n22 = t5.map((o4) => s99[o4.id]), i9 = t5.map((o4) => o4.type), r2 = n22.filter((o4) => !(o4 & 1)), l11 = s99[e4.id] >> 1;
  function h3(o4) {
    let a2 = [];
    for (let f2 = 0; f2 < n22.length; f2++) {
      let u5 = se8(o4, n22[f2]);
      if (i9[f2] == 2) for (let d5 of u5) a2.push(d5);
      else a2.push(u5);
    }
    return e4.combine(a2);
  }
  return {
    create(o4) {
      for (let a2 of n22) U8(o4, a2);
      return o4.values[l11] = h3(o4), 1;
    },
    update(o4, a2) {
      if (!de7(o4, r2)) return 0;
      let f2 = h3(o4);
      return e4.compare(f2, o4.values[l11]) ? 0 : (o4.values[l11] = f2, 1);
    },
    reconfigure(o4, a2) {
      let f2 = de7(o4, n22), u5 = a2.config.facets[e4.id], d5 = a2.facet(e4);
      if (u5 && !f2 && Ie6(t5, u5)) return o4.values[l11] = d5, 0;
      let c4 = h3(o4);
      return e4.compare(c4, d5) ? (o4.values[l11] = d5, 0) : (o4.values[l11] = c4, 1);
    }
  };
}
var Q8 = k7.define({
  static: true
});
var z8 = class s54 {
  constructor(e4, t5, n22, i9, r2) {
    this.id = e4, this.createF = t5, this.updateF = n22, this.compareF = i9, this.spec = r2, this.provides = void 0;
  }
  static define(e4) {
    let t5 = new s54(Se7++, e4.create, e4.update, e4.compare || ((n22, i9) => n22 === i9), e4);
    return e4.provide && (t5.provides = e4.provide(t5)), t5;
  }
  create(e4) {
    let t5 = e4.facet(Q8).find((n22) => n22.field == this);
    return (t5?.create || this.createF)(e4);
  }
  slot(e4) {
    let t5 = e4[this.id] >> 1;
    return {
      create: (n22) => (n22.values[t5] = this.create(n22), 1),
      update: (n22, i9) => {
        let r2 = n22.values[t5], l11 = this.updateF(r2, i9);
        return this.compareF(r2, l11) ? 0 : (n22.values[t5] = l11, 1);
      },
      reconfigure: (n22, i9) => {
        let r2 = n22.facet(Q8), l11 = i9.facet(Q8), h3;
        return (h3 = r2.find((o4) => o4.field == this)) && h3 != l11.find((o4) => o4.field == this) ? (n22.values[t5] = h3.create(n22), 1) : i9.config.address[this.id] != null ? (n22.values[t5] = i9.field(this), 0) : (n22.values[t5] = this.create(n22), 1);
      }
    };
  }
  init(e4) {
    return [
      this,
      Q8.of({
        field: this,
        create: e4
      })
    ];
  }
  get extension() {
    return this;
  }
};
var b7 = {
  lowest: 4,
  low: 3,
  default: 2,
  high: 1,
  highest: 0
};
function W7(s99) {
  return (e4) => new te7(e4, s99);
}
var st4 = {
  highest: W7(b7.highest),
  high: W7(b7.high),
  default: W7(b7.default),
  low: W7(b7.low),
  lowest: W7(b7.lowest)
};
var te7 = class {
  constructor(e4, t5) {
    this.inner = e4, this.prec = t5;
  }
};
var ne7 = class s55 {
  of(e4) {
    return new G6(this, e4);
  }
  reconfigure(e4) {
    return s55.reconfigure.of({
      compartment: this,
      extension: e4
    });
  }
  get(e4) {
    return e4.config.compartments.get(this);
  }
};
var G6 = class {
  constructor(e4, t5) {
    this.compartment = e4, this.inner = t5;
  }
};
var ie7 = class s56 {
  constructor(e4, t5, n22, i9, r2, l11) {
    for (this.base = e4, this.compartments = t5, this.dynamicSlots = n22, this.address = i9, this.staticValues = r2, this.facets = l11, this.statusTemplate = []; this.statusTemplate.length < n22.length; ) this.statusTemplate.push(0);
  }
  staticFacet(e4) {
    let t5 = this.address[e4.id];
    return t5 == null ? e4.default : this.staticValues[t5 >> 1];
  }
  static resolve(e4, t5, n22) {
    let i9 = [], r2 = /* @__PURE__ */ Object.create(null), l11 = /* @__PURE__ */ new Map();
    for (let d5 of Ge4(e4, t5, l11)) d5 instanceof z8 ? i9.push(d5) : (r2[d5.facet.id] || (r2[d5.facet.id] = [])).push(d5);
    let h3 = /* @__PURE__ */ Object.create(null), o4 = [], a2 = [];
    for (let d5 of i9) h3[d5.id] = a2.length << 1, a2.push((c4) => d5.slot(c4));
    let f2 = n22?.config.facets;
    for (let d5 in r2) {
      let c4 = r2[d5], g6 = c4[0].facet, I13 = f2 && f2[d5] || [];
      if (c4.every((p5) => p5.type == 0)) if (h3[g6.id] = o4.length << 1 | 1, Ie6(I13, c4)) o4.push(n22.facet(g6));
      else {
        let p5 = g6.combine(c4.map((he10) => he10.value));
        o4.push(n22 && g6.compare(p5, n22.facet(g6)) ? n22.facet(g6) : p5);
      }
      else {
        for (let p5 of c4) p5.type == 0 ? (h3[p5.id] = o4.length << 1 | 1, o4.push(p5.value)) : (h3[p5.id] = a2.length << 1, a2.push((he10) => p5.dynamicSlot(he10)));
        h3[g6.id] = a2.length << 1, a2.push((p5) => Ue5(p5, g6, c4));
      }
    }
    let u5 = a2.map((d5) => d5(h3));
    return new s56(e4, l11, u5, h3, o4, r2);
  }
};
function Ge4(s99, e4, t5) {
  let n22 = [
    [],
    [],
    [],
    [],
    []
  ], i9 = /* @__PURE__ */ new Map();
  function r2(l11, h3) {
    let o4 = i9.get(l11);
    if (o4 != null) {
      if (o4 <= h3) return;
      let a2 = n22[o4].indexOf(l11);
      a2 > -1 && n22[o4].splice(a2, 1), l11 instanceof G6 && t5.delete(l11.compartment);
    }
    if (i9.set(l11, h3), Array.isArray(l11)) for (let a2 of l11) r2(a2, h3);
    else if (l11 instanceof G6) {
      if (t5.has(l11.compartment)) throw new RangeError("Duplicate use of compartment in extensions");
      let a2 = e4.get(l11.compartment) || l11.inner;
      t5.set(l11.compartment, a2), r2(a2, h3);
    } else if (l11 instanceof te7) r2(l11.inner, l11.prec);
    else if (l11 instanceof z8) n22[h3].push(l11), l11.provides && r2(l11.provides, h3);
    else if (l11 instanceof D6) n22[h3].push(l11), l11.facet.extensions && r2(l11.facet.extensions, b7.default);
    else {
      let a2 = l11.extension;
      if (!a2) throw new Error(`Unrecognized extension value in extension set (${l11}). This sometimes happens because multiple instances of @codemirror/state are loaded, breaking instanceof checks.`);
      r2(a2, h3);
    }
  }
  return r2(s99, b7.default), n22.reduce((l11, h3) => l11.concat(h3));
}
function U8(s99, e4) {
  if (e4 & 1) return 2;
  let t5 = e4 >> 1, n22 = s99.status[t5];
  if (n22 == 4) throw new Error("Cyclic dependency between fields and/or facets");
  if (n22 & 2) return n22;
  s99.status[t5] = 4;
  let i9 = s99.computeSlot(s99, s99.config.dynamicSlots[t5]);
  return s99.status[t5] = 2 | i9;
}
function se8(s99, e4) {
  return e4 & 1 ? s99.config.staticValues[e4 >> 1] : s99.values[e4 >> 1];
}
var Be6 = k7.define();
var ge6 = k7.define({
  combine: (s99) => s99.some((e4) => e4),
  static: true
});
var Ce7 = k7.define({
  combine: (s99) => s99.length ? s99[0] : void 0,
  static: true
});
var Fe6 = k7.define();
var Le7 = k7.define();
var Ne4 = k7.define();
var Je5 = k7.define({
  combine: (s99) => s99.length ? s99[0] : false
});
var L7 = class {
  constructor(e4, t5) {
    this.type = e4, this.value = t5;
  }
  static define() {
    return new pe6();
  }
};
var pe6 = class {
  of(e4) {
    return new L7(this, e4);
  }
};
var me6 = class {
  constructor(e4) {
    this.map = e4;
  }
  of(e4) {
    return new v5(this, e4);
  }
};
var v5 = class s57 {
  constructor(e4, t5) {
    this.type = e4, this.value = t5;
  }
  map(e4) {
    let t5 = this.type.map(this.value, e4);
    return t5 === void 0 ? void 0 : t5 == this.value ? this : new s57(this.type, t5);
  }
  is(e4) {
    return this.type == e4;
  }
  static define(e4 = {}) {
    return new me6(e4.map || ((t5) => t5));
  }
  static mapEffects(e4, t5) {
    if (!e4.length) return e4;
    let n22 = [];
    for (let i9 of e4) {
      let r2 = i9.map(t5);
      r2 && n22.push(r2);
    }
    return n22;
  }
};
v5.reconfigure = v5.define();
v5.appendConfig = v5.define();
var S7 = class s58 {
  constructor(e4, t5, n22, i9, r2, l11) {
    this.startState = e4, this.changes = t5, this.selection = n22, this.effects = i9, this.annotations = r2, this.scrollIntoView = l11, this._doc = null, this._state = null, n22 && Re6(n22, t5.newLength), r2.some((h3) => h3.type == s58.time) || (this.annotations = r2.concat(s58.time.of(Date.now())));
  }
  static create(e4, t5, n22, i9, r2, l11) {
    return new s58(e4, t5, n22, i9, r2, l11);
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
  annotation(e4) {
    for (let t5 of this.annotations) if (t5.type == e4) return t5.value;
  }
  get docChanged() {
    return !this.changes.empty;
  }
  get reconfigured() {
    return this.startState.config != this.state.config;
  }
  isUserEvent(e4) {
    let t5 = this.annotation(s58.userEvent);
    return !!(t5 && (t5 == e4 || t5.length > e4.length && t5.slice(0, e4.length) == e4 && t5[e4.length] == "."));
  }
};
S7.time = L7.define();
S7.userEvent = L7.define();
S7.addToHistory = L7.define();
S7.remote = L7.define();
function He4(s99, e4) {
  let t5 = [];
  for (let n22 = 0, i9 = 0; ; ) {
    let r2, l11;
    if (n22 < s99.length && (i9 == e4.length || e4[i9] >= s99[n22])) r2 = s99[n22++], l11 = s99[n22++];
    else if (i9 < e4.length) r2 = e4[i9++], l11 = e4[i9++];
    else return t5;
    !t5.length || t5[t5.length - 1] < r2 ? t5.push(r2, l11) : t5[t5.length - 1] < l11 && (t5[t5.length - 1] = l11);
  }
}
function De7(s99, e4, t5) {
  var n22;
  let i9, r2, l11;
  return t5 ? (i9 = e4.changes, r2 = A8.empty(e4.changes.length), l11 = s99.changes.compose(e4.changes)) : (i9 = e4.changes.map(s99.changes), r2 = s99.changes.mapDesc(e4.changes, true), l11 = s99.changes.compose(i9)), {
    changes: l11,
    selection: e4.selection ? e4.selection.map(r2) : (n22 = s99.selection) === null || n22 === void 0 ? void 0 : n22.map(i9),
    effects: v5.mapEffects(s99.effects, i9).concat(v5.mapEffects(e4.effects, r2)),
    annotations: s99.annotations.length ? s99.annotations.concat(e4.annotations) : e4.annotations,
    scrollIntoView: s99.scrollIntoView || e4.scrollIntoView
  };
}
function we5(s99, e4, t5) {
  let n22 = e4.selection, i9 = V9(e4.annotations);
  return e4.userEvent && (i9 = i9.concat(S7.userEvent.of(e4.userEvent))), {
    changes: e4.changes instanceof A8 ? e4.changes : A8.of(e4.changes || [], t5, s99.facet(Ce7)),
    selection: n22 && (n22 instanceof x8 ? n22 : x8.single(n22.anchor, n22.head)),
    effects: V9(e4.effects),
    annotations: i9,
    scrollIntoView: !!e4.scrollIntoView
  };
}
function Ve4(s99, e4, t5) {
  let n22 = we5(s99, e4.length ? e4[0] : {}, s99.doc.length);
  e4.length && e4[0].filter === false && (t5 = false);
  for (let r2 = 1; r2 < e4.length; r2++) {
    e4[r2].filter === false && (t5 = false);
    let l11 = !!e4[r2].sequential;
    n22 = De7(n22, we5(s99, e4[r2], l11 ? n22.changes.newLength : s99.doc.length), l11);
  }
  let i9 = S7.create(s99, n22.changes, n22.selection, n22.effects, n22.annotations, n22.scrollIntoView);
  return Qe4(t5 ? Ke4(i9) : i9);
}
function Ke4(s99) {
  let e4 = s99.startState, t5 = true;
  for (let i9 of e4.facet(Fe6)) {
    let r2 = i9(s99);
    if (r2 === false) {
      t5 = false;
      break;
    }
    Array.isArray(r2) && (t5 = t5 === true ? r2 : He4(t5, r2));
  }
  if (t5 !== true) {
    let i9, r2;
    if (t5 === false) r2 = s99.changes.invertedDesc, i9 = A8.empty(e4.doc.length);
    else {
      let l11 = s99.changes.filter(t5);
      i9 = l11.changes, r2 = l11.filtered.mapDesc(l11.changes).invertedDesc;
    }
    s99 = S7.create(e4, i9, s99.selection && s99.selection.map(r2), v5.mapEffects(s99.effects, r2), s99.annotations, s99.scrollIntoView);
  }
  let n22 = e4.facet(Le7);
  for (let i9 = n22.length - 1; i9 >= 0; i9--) {
    let r2 = n22[i9](s99);
    r2 instanceof S7 ? s99 = r2 : Array.isArray(r2) && r2.length == 1 && r2[0] instanceof S7 ? s99 = r2[0] : s99 = Ve4(e4, V9(r2), false);
  }
  return s99;
}
function Qe4(s99) {
  let e4 = s99.startState, t5 = e4.facet(Ne4), n22 = s99;
  for (let i9 = t5.length - 1; i9 >= 0; i9--) {
    let r2 = t5[i9](s99);
    r2 && Object.keys(r2).length && (n22 = De7(n22, we5(e4, r2, s99.changes.newLength), true));
  }
  return n22 == s99 ? s99 : S7.create(e4, s99.changes, s99.selection, n22.effects, n22.annotations, n22.scrollIntoView);
}
var Xe5 = [];
function V9(s99) {
  return s99 == null ? Xe5 : Array.isArray(s99) ? s99 : [
    s99
  ];
}
var M9 = function(s99) {
  return s99[s99.Word = 0] = "Word", s99[s99.Space = 1] = "Space", s99[s99.Other = 2] = "Other", s99;
}(M9 || (M9 = {}));
var Ye5 = /[\u00df\u0587\u0590-\u05f4\u0600-\u06ff\u3040-\u309f\u30a0-\u30ff\u3400-\u4db5\u4e00-\u9fcc\uac00-\ud7af]/;
var ve6;
try {
  ve6 = new RegExp("[\\p{Alphabetic}\\p{Number}_]", "u");
} catch {
}
function Ze4(s99) {
  if (ve6) return ve6.test(s99);
  for (let e4 = 0; e4 < s99.length; e4++) {
    let t5 = s99[e4];
    if (/\w/.test(t5) || t5 > "\x80" && (t5.toUpperCase() != t5.toLowerCase() || Ye5.test(t5))) return true;
  }
  return false;
}
function je4(s99) {
  return (e4) => {
    if (!/\S/.test(e4)) return M9.Space;
    if (Ze4(e4)) return M9.Word;
    for (let t5 = 0; t5 < s99.length; t5++) if (e4.indexOf(s99[t5]) > -1) return M9.Word;
    return M9.Other;
  };
}
var P7 = class s59 {
  constructor(e4, t5, n22, i9, r2, l11) {
    this.config = e4, this.doc = t5, this.selection = n22, this.values = i9, this.status = e4.statusTemplate.slice(), this.computeSlot = r2, l11 && (l11._state = this);
    for (let h3 = 0; h3 < this.config.dynamicSlots.length; h3++) U8(this, h3 << 1);
    this.computeSlot = null;
  }
  field(e4, t5 = true) {
    let n22 = this.config.address[e4.id];
    if (n22 == null) {
      if (t5) throw new RangeError("Field is not present in this state");
      return;
    }
    return U8(this, n22), se8(this, n22);
  }
  update(...e4) {
    return Ve4(this, e4, true);
  }
  applyTransaction(e4) {
    let t5 = this.config, { base: n22, compartments: i9 } = t5;
    for (let h3 of e4.effects) h3.is(ne7.reconfigure) ? (t5 && (i9 = /* @__PURE__ */ new Map(), t5.compartments.forEach((o4, a2) => i9.set(a2, o4)), t5 = null), i9.set(h3.value.compartment, h3.value.extension)) : h3.is(v5.reconfigure) ? (t5 = null, n22 = h3.value) : h3.is(v5.appendConfig) && (t5 = null, n22 = V9(n22).concat(h3.value));
    let r2;
    t5 ? r2 = e4.startState.values.slice() : (t5 = ie7.resolve(n22, i9, this), r2 = new s59(t5, this.doc, this.selection, t5.dynamicSlots.map(() => null), (o4, a2) => a2.reconfigure(o4, this), null).values);
    let l11 = e4.startState.facet(ge6) ? e4.newSelection : e4.newSelection.asSingle();
    new s59(t5, e4.newDoc, l11, r2, (h3, o4) => o4.update(h3, e4), e4);
  }
  replaceSelection(e4) {
    return typeof e4 == "string" && (e4 = this.toText(e4)), this.changeByRange((t5) => ({
      changes: {
        from: t5.from,
        to: t5.to,
        insert: e4
      },
      range: x8.cursor(t5.from + e4.length)
    }));
  }
  changeByRange(e4) {
    let t5 = this.selection, n22 = e4(t5.ranges[0]), i9 = this.changes(n22.changes), r2 = [
      n22.range
    ], l11 = V9(n22.effects);
    for (let h3 = 1; h3 < t5.ranges.length; h3++) {
      let o4 = e4(t5.ranges[h3]), a2 = this.changes(o4.changes), f2 = a2.map(i9);
      for (let d5 = 0; d5 < h3; d5++) r2[d5] = r2[d5].map(f2);
      let u5 = i9.mapDesc(a2, true);
      r2.push(o4.range.map(u5)), i9 = i9.compose(f2), l11 = v5.mapEffects(l11, f2).concat(v5.mapEffects(V9(o4.effects), u5));
    }
    return {
      changes: i9,
      selection: x8.create(r2, t5.mainIndex),
      effects: l11
    };
  }
  changes(e4 = []) {
    return e4 instanceof A8 ? e4 : A8.of(e4, this.doc.length, this.facet(s59.lineSeparator));
  }
  toText(e4) {
    return m7.of(e4.split(this.facet(s59.lineSeparator) || fe6));
  }
  sliceDoc(e4 = 0, t5 = this.doc.length) {
    return this.doc.sliceString(e4, t5, this.lineBreak);
  }
  facet(e4) {
    let t5 = this.config.address[e4.id];
    return t5 == null ? e4.default : (U8(this, t5), se8(this, t5));
  }
  toJSON(e4) {
    let t5 = {
      doc: this.sliceDoc(),
      selection: this.selection.toJSON()
    };
    if (e4) for (let n22 in e4) {
      let i9 = e4[n22];
      i9 instanceof z8 && this.config.address[i9.id] != null && (t5[n22] = i9.spec.toJSON(this.field(e4[n22]), this));
    }
    return t5;
  }
  static fromJSON(e4, t5 = {}, n22) {
    if (!e4 || typeof e4.doc != "string") throw new RangeError("Invalid JSON representation for EditorState");
    let i9 = [];
    if (n22) {
      for (let r2 in n22) if (Object.prototype.hasOwnProperty.call(e4, r2)) {
        let l11 = n22[r2], h3 = e4[r2];
        i9.push(l11.init((o4) => l11.spec.fromJSON(h3, o4)));
      }
    }
    return s59.create({
      doc: e4.doc,
      selection: x8.fromJSON(e4.selection),
      extensions: t5.extensions ? i9.concat([
        t5.extensions
      ]) : i9
    });
  }
  static create(e4 = {}) {
    let t5 = ie7.resolve(e4.extensions || [], /* @__PURE__ */ new Map()), n22 = e4.doc instanceof m7 ? e4.doc : m7.of((e4.doc || "").split(t5.staticFacet(s59.lineSeparator) || fe6)), i9 = e4.selection ? e4.selection instanceof x8 ? e4.selection : x8.single(e4.selection.anchor, e4.selection.head) : x8.single(0);
    return Re6(i9, n22.length), t5.staticFacet(ge6) || (i9 = i9.asSingle()), new s59(t5, n22, i9, t5.dynamicSlots.map(() => null), (r2, l11) => l11.create(r2), null);
  }
  get tabSize() {
    return this.facet(s59.tabSize);
  }
  get lineBreak() {
    return this.facet(s59.lineSeparator) || `
`;
  }
  get readOnly() {
    return this.facet(Je5);
  }
  phrase(e4, ...t5) {
    for (let n22 of this.facet(s59.phrases)) if (Object.prototype.hasOwnProperty.call(n22, e4)) {
      e4 = n22[e4];
      break;
    }
    return t5.length && (e4 = e4.replace(/\$(\$|\d*)/g, (n22, i9) => {
      if (i9 == "$") return "$";
      let r2 = +(i9 || 1);
      return !r2 || r2 > t5.length ? n22 : t5[r2 - 1];
    })), e4;
  }
  languageDataAt(e4, t5, n22 = -1) {
    let i9 = [];
    for (let r2 of this.facet(Be6)) for (let l11 of r2(this, t5, n22)) Object.prototype.hasOwnProperty.call(l11, e4) && i9.push(l11[e4]);
    return i9;
  }
  charCategorizer(e4) {
    let t5 = this.languageDataAt("wordChars", e4);
    return je4(t5.length ? t5[0] : "");
  }
  wordAt(e4) {
    let { text: t5, from: n22, length: i9 } = this.doc.lineAt(e4), r2 = this.charCategorizer(e4), l11 = e4 - n22, h3 = e4 - n22;
    for (; l11 > 0; ) {
      let o4 = ee6(t5, l11, false);
      if (r2(t5.slice(o4, l11)) != M9.Word) break;
      l11 = o4;
    }
    for (; h3 < i9; ) {
      let o4 = ee6(t5, h3);
      if (r2(t5.slice(h3, o4)) != M9.Word) break;
      h3 = o4;
    }
    return l11 == h3 ? null : x8.range(l11 + n22, h3 + n22);
  }
};
P7.allowMultipleSelections = ge6;
P7.tabSize = k7.define({
  combine: (s99) => s99.length ? s99[0] : 4
});
P7.lineSeparator = Ce7;
P7.readOnly = Je5;
P7.phrases = k7.define({
  compare(s99, e4) {
    let t5 = Object.keys(s99), n22 = Object.keys(e4);
    return t5.length == n22.length && t5.every((i9) => s99[i9] == e4[i9]);
  }
});
P7.languageData = Be6;
P7.changeFilter = Fe6;
P7.transactionFilter = Le7;
P7.transactionExtender = Ne4;
ne7.reconfigure = v5.define();
function rt4(s99, e4, t5 = {}) {
  let n22 = {};
  for (let i9 of s99) for (let r2 of Object.keys(i9)) {
    let l11 = i9[r2], h3 = n22[r2];
    if (h3 === void 0) n22[r2] = l11;
    else if (!(h3 === l11 || l11 === void 0)) if (Object.hasOwnProperty.call(t5, r2)) n22[r2] = t5[r2](h3, l11);
    else throw new Error("Config merge conflict for field " + r2);
  }
  for (let i9 in e4) n22[i9] === void 0 && (n22[i9] = e4[i9]);
  return n22;
}
var q7 = class {
  eq(e4) {
    return this == e4;
  }
  range(e4, t5 = e4) {
    return H7.create(e4, t5, this);
  }
};
q7.prototype.startSide = q7.prototype.endSide = 0;
q7.prototype.point = false;
q7.prototype.mapMode = E6.TrackDel;
function Pe7(s99, e4) {
  return s99 == e4 || s99.constructor == e4.constructor && s99.eq(e4);
}
var H7 = class s60 {
  constructor(e4, t5, n22) {
    this.from = e4, this.to = t5, this.value = n22;
  }
  static create(e4, t5, n22) {
    return new s60(e4, t5, n22);
  }
};
function xe7(s99, e4) {
  return s99.from - e4.from || s99.value.startSide - e4.value.startSide;
}
var ye6 = class s61 {
  constructor(e4, t5, n22, i9) {
    this.from = e4, this.to = t5, this.value = n22, this.maxPoint = i9;
  }
  get length() {
    return this.to[this.to.length - 1];
  }
  findIndex(e4, t5, n22, i9 = 0) {
    let r2 = n22 ? this.to : this.from;
    for (let l11 = i9, h3 = r2.length; ; ) {
      if (l11 == h3) return l11;
      let o4 = l11 + h3 >> 1, a2 = r2[o4] - e4 || (n22 ? this.value[o4].endSide : this.value[o4].startSide) - t5;
      if (o4 == l11) return a2 >= 0 ? l11 : h3;
      a2 >= 0 ? h3 = o4 : l11 = o4 + 1;
    }
  }
  between(e4, t5, n22, i9) {
    for (let r2 = this.findIndex(t5, -1e9, true), l11 = this.findIndex(n22, 1e9, false, r2); r2 < l11; r2++) if (i9(this.from[r2] + e4, this.to[r2] + e4, this.value[r2]) === false) return false;
  }
  map(e4, t5) {
    let n22 = [], i9 = [], r2 = [], l11 = -1, h3 = -1;
    for (let o4 = 0; o4 < this.value.length; o4++) {
      let a2 = this.value[o4], f2 = this.from[o4] + e4, u5 = this.to[o4] + e4, d5, c4;
      if (f2 == u5) {
        let g6 = t5.mapPos(f2, a2.startSide, a2.mapMode);
        if (g6 == null || (d5 = c4 = g6, a2.startSide != a2.endSide && (c4 = t5.mapPos(f2, a2.endSide), c4 < d5))) continue;
      } else if (d5 = t5.mapPos(f2, a2.startSide), c4 = t5.mapPos(u5, a2.endSide), d5 > c4 || d5 == c4 && a2.startSide > 0 && a2.endSide <= 0) continue;
      (c4 - d5 || a2.endSide - a2.startSide) < 0 || (l11 < 0 && (l11 = d5), a2.point && (h3 = Math.max(h3, c4 - d5)), n22.push(a2), i9.push(d5 - l11), r2.push(c4 - l11));
    }
    return {
      mapped: n22.length ? new s61(i9, r2, n22, h3) : null,
      pos: l11
    };
  }
};
var T7 = class s62 {
  constructor(e4, t5, n22, i9) {
    this.chunkPos = e4, this.chunk = t5, this.nextLayer = n22, this.maxPoint = i9;
  }
  static create(e4, t5, n22, i9) {
    return new s62(e4, t5, n22, i9);
  }
  get length() {
    let e4 = this.chunk.length - 1;
    return e4 < 0 ? 0 : Math.max(this.chunkEnd(e4), this.nextLayer.length);
  }
  get size() {
    if (this.isEmpty) return 0;
    let e4 = this.nextLayer.size;
    for (let t5 of this.chunk) e4 += t5.value.length;
    return e4;
  }
  chunkEnd(e4) {
    return this.chunkPos[e4] + this.chunk[e4].length;
  }
  update(e4) {
    let { add: t5 = [], sort: n22 = false, filterFrom: i9 = 0, filterTo: r2 = this.length } = e4, l11 = e4.filter;
    if (t5.length == 0 && !l11) return this;
    if (n22 && (t5 = t5.slice().sort(xe7)), this.isEmpty) return t5.length ? s62.of(t5) : this;
    let h3 = new le7(this, null, -1).goto(0), o4 = 0, a2 = [], f2 = new re7();
    for (; h3.value || o4 < t5.length; ) if (o4 < t5.length && (h3.from - t5[o4].from || h3.startSide - t5[o4].value.startSide) >= 0) {
      let u5 = t5[o4++];
      f2.addInner(u5.from, u5.to, u5.value) || a2.push(u5);
    } else h3.rangeIndex == 1 && h3.chunkIndex < this.chunk.length && (o4 == t5.length || this.chunkEnd(h3.chunkIndex) < t5[o4].from) && (!l11 || i9 > this.chunkEnd(h3.chunkIndex) || r2 < this.chunkPos[h3.chunkIndex]) && f2.addChunk(this.chunkPos[h3.chunkIndex], this.chunk[h3.chunkIndex]) ? h3.nextChunk() : ((!l11 || i9 > h3.to || r2 < h3.from || l11(h3.from, h3.to, h3.value)) && (f2.addInner(h3.from, h3.to, h3.value) || a2.push(H7.create(h3.from, h3.to, h3.value))), h3.next());
    return f2.finishInner(this.nextLayer.isEmpty && !a2.length ? s62.empty : this.nextLayer.update({
      add: a2,
      filter: l11,
      filterFrom: i9,
      filterTo: r2
    }));
  }
  map(e4) {
    if (e4.empty || this.isEmpty) return this;
    let t5 = [], n22 = [], i9 = -1;
    for (let l11 = 0; l11 < this.chunk.length; l11++) {
      let h3 = this.chunkPos[l11], o4 = this.chunk[l11], a2 = e4.touchesRange(h3, h3 + o4.length);
      if (a2 === false) i9 = Math.max(i9, o4.maxPoint), t5.push(o4), n22.push(e4.mapPos(h3));
      else if (a2 === true) {
        let { mapped: f2, pos: u5 } = o4.map(h3, e4);
        f2 && (i9 = Math.max(i9, f2.maxPoint), t5.push(f2), n22.push(u5));
      }
    }
    let r2 = this.nextLayer.map(e4);
    return t5.length == 0 ? r2 : new s62(n22, t5, r2 || s62.empty, i9);
  }
  between(e4, t5, n22) {
    if (!this.isEmpty) {
      for (let i9 = 0; i9 < this.chunk.length; i9++) {
        let r2 = this.chunkPos[i9], l11 = this.chunk[i9];
        if (t5 >= r2 && e4 <= r2 + l11.length && l11.between(r2, e4 - r2, t5 - r2, n22) === false) return;
      }
      this.nextLayer.between(e4, t5, n22);
    }
  }
  iter(e4 = 0) {
    return K8.from([
      this
    ]).goto(e4);
  }
  get isEmpty() {
    return this.nextLayer == this;
  }
  static iter(e4, t5 = 0) {
    return K8.from(e4).goto(t5);
  }
  static compare(e4, t5, n22, i9, r2 = -1) {
    let l11 = e4.filter((u5) => u5.maxPoint > 0 || !u5.isEmpty && u5.maxPoint >= r2), h3 = t5.filter((u5) => u5.maxPoint > 0 || !u5.isEmpty && u5.maxPoint >= r2), o4 = Oe5(l11, h3, n22), a2 = new R8(l11, o4, r2), f2 = new R8(h3, o4, r2);
    n22.iterGaps((u5, d5, c4) => Me6(a2, u5, f2, d5, c4, i9)), n22.empty && n22.length == 0 && Me6(a2, 0, f2, 0, 0, i9);
  }
  static eq(e4, t5, n22 = 0, i9) {
    i9 == null && (i9 = 999999999);
    let r2 = e4.filter((f2) => !f2.isEmpty && t5.indexOf(f2) < 0), l11 = t5.filter((f2) => !f2.isEmpty && e4.indexOf(f2) < 0);
    if (r2.length != l11.length) return false;
    if (!r2.length) return true;
    let h3 = Oe5(r2, l11), o4 = new R8(r2, h3, 0).goto(n22), a2 = new R8(l11, h3, 0).goto(n22);
    for (; ; ) {
      if (o4.to != a2.to || !ke7(o4.active, a2.active) || o4.point && (!a2.point || !Pe7(o4.point, a2.point))) return false;
      if (o4.to > i9) return true;
      o4.next(), a2.next();
    }
  }
  static spans(e4, t5, n22, i9, r2 = -1) {
    let l11 = new R8(e4, null, r2).goto(t5), h3 = t5, o4 = l11.openStart;
    for (; ; ) {
      let a2 = Math.min(l11.to, n22);
      if (l11.point) {
        let f2 = l11.activeForPoint(l11.to), u5 = l11.pointFrom < t5 ? f2.length + 1 : l11.point.startSide < 0 ? f2.length : Math.min(f2.length, o4);
        i9.point(h3, a2, l11.point, f2, u5, l11.pointRank), o4 = Math.min(l11.openEnd(a2), f2.length);
      } else a2 > h3 && (i9.span(h3, a2, l11.active, o4), o4 = l11.openEnd(a2));
      if (l11.to > n22) return o4 + (l11.point && l11.to > n22 ? 1 : 0);
      h3 = l11.to, l11.next();
    }
  }
  static of(e4, t5 = false) {
    let n22 = new re7();
    for (let i9 of e4 instanceof H7 ? [
      e4
    ] : t5 ? _e6(e4) : e4) n22.add(i9.from, i9.to, i9.value);
    return n22.finish();
  }
  static join(e4) {
    if (!e4.length) return s62.empty;
    let t5 = e4[e4.length - 1];
    for (let n22 = e4.length - 2; n22 >= 0; n22--) for (let i9 = e4[n22]; i9 != s62.empty; i9 = i9.nextLayer) t5 = new s62(i9.chunkPos, i9.chunk, t5, Math.max(i9.maxPoint, t5.maxPoint));
    return t5;
  }
};
T7.empty = new T7([], [], null, -1);
function _e6(s99) {
  if (s99.length > 1) for (let e4 = s99[0], t5 = 1; t5 < s99.length; t5++) {
    let n22 = s99[t5];
    if (xe7(e4, n22) > 0) return s99.slice().sort(xe7);
    e4 = n22;
  }
  return s99;
}
T7.empty.nextLayer = T7.empty;
var re7 = class s63 {
  finishChunk(e4) {
    this.chunks.push(new ye6(this.from, this.to, this.value, this.maxPoint)), this.chunkPos.push(this.chunkStart), this.chunkStart = -1, this.setMaxPoint = Math.max(this.setMaxPoint, this.maxPoint), this.maxPoint = -1, e4 && (this.from = [], this.to = [], this.value = []);
  }
  constructor() {
    this.chunks = [], this.chunkPos = [], this.chunkStart = -1, this.last = null, this.lastFrom = -1e9, this.lastTo = -1e9, this.from = [], this.to = [], this.value = [], this.maxPoint = -1, this.setMaxPoint = -1, this.nextLayer = null;
  }
  add(e4, t5, n22) {
    this.addInner(e4, t5, n22) || (this.nextLayer || (this.nextLayer = new s63())).add(e4, t5, n22);
  }
  addInner(e4, t5, n22) {
    let i9 = e4 - this.lastTo || n22.startSide - this.last.endSide;
    if (i9 <= 0 && (e4 - this.lastFrom || n22.startSide - this.last.startSide) < 0) throw new Error("Ranges must be added sorted by `from` position and `startSide`");
    return i9 < 0 ? false : (this.from.length == 250 && this.finishChunk(true), this.chunkStart < 0 && (this.chunkStart = e4), this.from.push(e4 - this.chunkStart), this.to.push(t5 - this.chunkStart), this.last = n22, this.lastFrom = e4, this.lastTo = t5, this.value.push(n22), n22.point && (this.maxPoint = Math.max(this.maxPoint, t5 - e4)), true);
  }
  addChunk(e4, t5) {
    if ((e4 - this.lastTo || t5.value[0].startSide - this.last.endSide) < 0) return false;
    this.from.length && this.finishChunk(true), this.setMaxPoint = Math.max(this.setMaxPoint, t5.maxPoint), this.chunks.push(t5), this.chunkPos.push(e4);
    let n22 = t5.value.length - 1;
    return this.last = t5.value[n22], this.lastFrom = t5.from[n22] + e4, this.lastTo = t5.to[n22] + e4, true;
  }
  finish() {
    return this.finishInner(T7.empty);
  }
  finishInner(e4) {
    if (this.from.length && this.finishChunk(false), this.chunks.length == 0) return e4;
    let t5 = T7.create(this.chunkPos, this.chunks, this.nextLayer ? this.nextLayer.finishInner(e4) : e4, this.setMaxPoint);
    return this.from = null, t5;
  }
};
function Oe5(s99, e4, t5) {
  let n22 = /* @__PURE__ */ new Map();
  for (let r2 of s99) for (let l11 = 0; l11 < r2.chunk.length; l11++) r2.chunk[l11].maxPoint <= 0 && n22.set(r2.chunk[l11], r2.chunkPos[l11]);
  let i9 = /* @__PURE__ */ new Set();
  for (let r2 of e4) for (let l11 = 0; l11 < r2.chunk.length; l11++) {
    let h3 = n22.get(r2.chunk[l11]);
    h3 != null && (t5 ? t5.mapPos(h3) : h3) == r2.chunkPos[l11] && !t5?.touchesRange(h3, h3 + r2.chunk[l11].length) && i9.add(r2.chunk[l11]);
  }
  return i9;
}
var le7 = class {
  constructor(e4, t5, n22, i9 = 0) {
    this.layer = e4, this.skip = t5, this.minPoint = n22, this.rank = i9;
  }
  get startSide() {
    return this.value ? this.value.startSide : 0;
  }
  get endSide() {
    return this.value ? this.value.endSide : 0;
  }
  goto(e4, t5 = -1e9) {
    return this.chunkIndex = this.rangeIndex = 0, this.gotoInner(e4, t5, false), this;
  }
  gotoInner(e4, t5, n22) {
    for (; this.chunkIndex < this.layer.chunk.length; ) {
      let i9 = this.layer.chunk[this.chunkIndex];
      if (!(this.skip && this.skip.has(i9) || this.layer.chunkEnd(this.chunkIndex) < e4 || i9.maxPoint < this.minPoint)) break;
      this.chunkIndex++, n22 = false;
    }
    if (this.chunkIndex < this.layer.chunk.length) {
      let i9 = this.layer.chunk[this.chunkIndex].findIndex(e4 - this.layer.chunkPos[this.chunkIndex], t5, true);
      (!n22 || this.rangeIndex < i9) && this.setRangeIndex(i9);
    }
    this.next();
  }
  forward(e4, t5) {
    (this.to - e4 || this.endSide - t5) < 0 && this.gotoInner(e4, t5, true);
  }
  next() {
    for (; ; ) if (this.chunkIndex == this.layer.chunk.length) {
      this.from = this.to = 1e9, this.value = null;
      break;
    } else {
      let e4 = this.layer.chunkPos[this.chunkIndex], t5 = this.layer.chunk[this.chunkIndex], n22 = e4 + t5.from[this.rangeIndex];
      if (this.from = n22, this.to = e4 + t5.to[this.rangeIndex], this.value = t5.value[this.rangeIndex], this.setRangeIndex(this.rangeIndex + 1), this.minPoint < 0 || this.value.point && this.to - this.from >= this.minPoint) break;
    }
  }
  setRangeIndex(e4) {
    if (e4 == this.layer.chunk[this.chunkIndex].value.length) {
      if (this.chunkIndex++, this.skip) for (; this.chunkIndex < this.layer.chunk.length && this.skip.has(this.layer.chunk[this.chunkIndex]); ) this.chunkIndex++;
      this.rangeIndex = 0;
    } else this.rangeIndex = e4;
  }
  nextChunk() {
    this.chunkIndex++, this.rangeIndex = 0, this.next();
  }
  compare(e4) {
    return this.from - e4.from || this.startSide - e4.startSide || this.rank - e4.rank || this.to - e4.to || this.endSide - e4.endSide;
  }
};
var K8 = class s64 {
  constructor(e4) {
    this.heap = e4;
  }
  static from(e4, t5 = null, n22 = -1) {
    let i9 = [];
    for (let r2 = 0; r2 < e4.length; r2++) for (let l11 = e4[r2]; !l11.isEmpty; l11 = l11.nextLayer) l11.maxPoint >= n22 && i9.push(new le7(l11, t5, n22, r2));
    return i9.length == 1 ? i9[0] : new s64(i9);
  }
  get startSide() {
    return this.value ? this.value.startSide : 0;
  }
  goto(e4, t5 = -1e9) {
    for (let n22 of this.heap) n22.goto(e4, t5);
    for (let n22 = this.heap.length >> 1; n22 >= 0; n22--) oe8(this.heap, n22);
    return this.next(), this;
  }
  forward(e4, t5) {
    for (let n22 of this.heap) n22.forward(e4, t5);
    for (let n22 = this.heap.length >> 1; n22 >= 0; n22--) oe8(this.heap, n22);
    (this.to - e4 || this.value.endSide - t5) < 0 && this.next();
  }
  next() {
    if (this.heap.length == 0) this.from = this.to = 1e9, this.value = null, this.rank = -1;
    else {
      let e4 = this.heap[0];
      this.from = e4.from, this.to = e4.to, this.value = e4.value, this.rank = e4.rank, e4.value && e4.next(), oe8(this.heap, 0);
    }
  }
};
function oe8(s99, e4) {
  for (let t5 = s99[e4]; ; ) {
    let n22 = (e4 << 1) + 1;
    if (n22 >= s99.length) break;
    let i9 = s99[n22];
    if (n22 + 1 < s99.length && i9.compare(s99[n22 + 1]) >= 0 && (i9 = s99[n22 + 1], n22++), t5.compare(i9) < 0) break;
    s99[n22] = t5, s99[e4] = i9, e4 = n22;
  }
}
var R8 = class {
  constructor(e4, t5, n22) {
    this.minPoint = n22, this.active = [], this.activeTo = [], this.activeRank = [], this.minActive = -1, this.point = null, this.pointFrom = 0, this.pointRank = 0, this.to = -1e9, this.endSide = 0, this.openStart = -1, this.cursor = K8.from(e4, t5, n22);
  }
  goto(e4, t5 = -1e9) {
    return this.cursor.goto(e4, t5), this.active.length = this.activeTo.length = this.activeRank.length = 0, this.minActive = -1, this.to = e4, this.endSide = t5, this.openStart = -1, this.next(), this;
  }
  forward(e4, t5) {
    for (; this.minActive > -1 && (this.activeTo[this.minActive] - e4 || this.active[this.minActive].endSide - t5) < 0; ) this.removeActive(this.minActive);
    this.cursor.forward(e4, t5);
  }
  removeActive(e4) {
    X8(this.active, e4), X8(this.activeTo, e4), X8(this.activeRank, e4), this.minActive = Te7(this.active, this.activeTo);
  }
  addActive(e4) {
    let t5 = 0, { value: n22, to: i9, rank: r2 } = this.cursor;
    for (; t5 < this.activeRank.length && (r2 - this.activeRank[t5] || i9 - this.activeTo[t5]) > 0; ) t5++;
    Y7(this.active, t5, n22), Y7(this.activeTo, t5, i9), Y7(this.activeRank, t5, r2), e4 && Y7(e4, t5, this.cursor.from), this.minActive = Te7(this.active, this.activeTo);
  }
  next() {
    let e4 = this.to, t5 = this.point;
    this.point = null;
    let n22 = this.openStart < 0 ? [] : null;
    for (; ; ) {
      let i9 = this.minActive;
      if (i9 > -1 && (this.activeTo[i9] - this.cursor.from || this.active[i9].endSide - this.cursor.startSide) < 0) {
        if (this.activeTo[i9] > e4) {
          this.to = this.activeTo[i9], this.endSide = this.active[i9].endSide;
          break;
        }
        this.removeActive(i9), n22 && X8(n22, i9);
      } else if (this.cursor.value) if (this.cursor.from > e4) {
        this.to = this.cursor.from, this.endSide = this.cursor.startSide;
        break;
      } else {
        let r2 = this.cursor.value;
        if (!r2.point) this.addActive(n22), this.cursor.next();
        else if (t5 && this.cursor.to == this.to && this.cursor.from < this.cursor.to) this.cursor.next();
        else {
          this.point = r2, this.pointFrom = this.cursor.from, this.pointRank = this.cursor.rank, this.to = this.cursor.to, this.endSide = r2.endSide, this.cursor.next(), this.forward(this.to, this.endSide);
          break;
        }
      }
      else {
        this.to = this.endSide = 1e9;
        break;
      }
    }
    if (n22) {
      this.openStart = 0;
      for (let i9 = n22.length - 1; i9 >= 0 && n22[i9] < e4; i9--) this.openStart++;
    }
  }
  activeForPoint(e4) {
    if (!this.active.length) return this.active;
    let t5 = [];
    for (let n22 = this.active.length - 1; n22 >= 0 && !(this.activeRank[n22] < this.pointRank); n22--) (this.activeTo[n22] > e4 || this.activeTo[n22] == e4 && this.active[n22].endSide >= this.point.endSide) && t5.push(this.active[n22]);
    return t5.reverse();
  }
  openEnd(e4) {
    let t5 = 0;
    for (let n22 = this.activeTo.length - 1; n22 >= 0 && this.activeTo[n22] > e4; n22--) t5++;
    return t5;
  }
};
function Me6(s99, e4, t5, n22, i9, r2) {
  s99.goto(e4), t5.goto(n22);
  let l11 = n22 + i9, h3 = n22, o4 = n22 - e4, a2 = !!r2.boundChange;
  for (let f2 = false; ; ) {
    let u5 = s99.to + o4 - t5.to, d5 = u5 || s99.endSide - t5.endSide, c4 = d5 < 0 ? s99.to + o4 : t5.to, g6 = Math.min(c4, l11);
    if (s99.point || t5.point ? (s99.point && t5.point && Pe7(s99.point, t5.point) && ke7(s99.activeForPoint(s99.to), t5.activeForPoint(t5.to)) || r2.comparePoint(h3, g6, s99.point, t5.point), f2 = false) : (f2 && r2.boundChange(h3), g6 > h3 && !ke7(s99.active, t5.active) && r2.compareRange(h3, g6, s99.active, t5.active), a2 && g6 < l11 && (u5 || s99.openEnd(c4) != t5.openEnd(c4)) && (f2 = true)), c4 > l11) break;
    h3 = c4, d5 <= 0 && s99.next(), d5 >= 0 && t5.next();
  }
}
function ke7(s99, e4) {
  if (s99.length != e4.length) return false;
  for (let t5 = 0; t5 < s99.length; t5++) if (s99[t5] != e4[t5] && !Pe7(s99[t5], e4[t5])) return false;
  return true;
}
function X8(s99, e4) {
  for (let t5 = e4, n22 = s99.length - 1; t5 < n22; t5++) s99[t5] = s99[t5 + 1];
  s99.pop();
}
function Y7(s99, e4, t5) {
  for (let n22 = s99.length - 1; n22 >= e4; n22--) s99[n22 + 1] = s99[n22];
  s99[e4] = t5;
}
function Te7(s99, e4) {
  let t5 = -1, n22 = 1e9;
  for (let i9 = 0; i9 < e4.length; i9++) (e4[i9] - n22 || s99[i9].endSide - s99[t5].endSide) < 0 && (t5 = i9, n22 = e4[i9]);
  return t5;
}
function lt4(s99, e4, t5 = s99.length) {
  let n22 = 0;
  for (let i9 = 0; i9 < t5 && i9 < s99.length; ) s99.charCodeAt(i9) == 9 ? (n22 += e4 - n22 % e4, i9++) : (n22++, i9 = ee6(s99, i9));
  return n22;
}
function ht5(s99, e4, t5, n22) {
  for (let i9 = 0, r2 = 0; ; ) {
    if (r2 >= e4) return i9;
    if (i9 == s99.length) break;
    r2 += s99.charCodeAt(i9) == 9 ? t5 - r2 % t5 : 1, i9 = ee6(s99, i9);
  }
  return n22 === true ? -1 : s99.length;
}

// deno:https://esm.sh/@codemirror/view@6.39.10/denonext/view.mjs
var W8 = typeof navigator < "u" ? navigator : {
  userAgent: "",
  vendor: "",
  platform: ""
};
var ti2 = typeof document < "u" ? document : {
  documentElement: {
    style: {}
  }
};
var ei2 = /Edge\/(\d+)/.exec(W8.userAgent);
var Gs2 = /MSIE \d/.test(W8.userAgent);
var ii2 = /Trident\/(?:[7-9]|\d{2,})\..*rv:(\d+)/.exec(W8.userAgent);
var ze6 = !!(Gs2 || ii2 || ei2);
var as = !ze6 && /gecko\/(\d+)/i.test(W8.userAgent);
var Ye6 = !ze6 && /Chrome\/(\d+)/.exec(W8.userAgent);
var hs = "webkitFontSmoothing" in ti2.documentElement.style;
var si2 = !ze6 && /Apple Computer/.test(W8.vendor);
var cs = si2 && (/Mobile\/\w+/.test(W8.userAgent) || W8.maxTouchPoints > 2);
var y8 = {
  mac: cs || /Mac/.test(W8.platform),
  windows: /Win/.test(W8.platform),
  linux: /Linux|X11/.test(W8.platform),
  ie: ze6,
  ie_version: Gs2 ? ti2.documentMode || 6 : ii2 ? +ii2[1] : ei2 ? +ei2[1] : 0,
  gecko: as,
  gecko_version: as ? +(/Firefox\/(\d+)/.exec(W8.userAgent) || [
    0,
    0
  ])[1] : 0,
  chrome: !!Ye6,
  chrome_version: Ye6 ? +Ye6[1] : 0,
  ios: cs,
  android: /Android\b/.test(W8.userAgent),
  webkit: hs,
  webkit_version: hs ? +(/\bAppleWebKit\/(\d+)/.exec(W8.userAgent) || [
    0,
    0
  ])[1] : 0,
  safari: si2,
  safari_version: si2 ? +(/\bVersion\/(\d+(\.\d+)?)/.exec(W8.userAgent) || [
    0,
    0
  ])[1] : 0,
  tabSize: ti2.documentElement.style.tabSize != null ? "tab-size" : "-moz-tab-size"
};
function Zi2(s99, t5) {
  for (let e4 in s99) e4 == "class" && t5.class ? t5.class += " " + s99.class : e4 == "style" && t5.style ? t5.style += ";" + s99.style : t5[e4] = s99[e4];
  return t5;
}
var Me7 = /* @__PURE__ */ Object.create(null);
function ts2(s99, t5, e4) {
  if (s99 == t5) return true;
  s99 || (s99 = Me7), t5 || (t5 = Me7);
  let i9 = Object.keys(s99), n22 = Object.keys(t5);
  if (i9.length - (e4 && i9.indexOf(e4) > -1 ? 1 : 0) != n22.length - (e4 && n22.indexOf(e4) > -1 ? 1 : 0)) return false;
  for (let o4 of i9) if (o4 != e4 && (n22.indexOf(o4) == -1 || s99[o4] !== t5[o4])) return false;
  return true;
}
function ho2(s99, t5) {
  for (let e4 = s99.attributes.length - 1; e4 >= 0; e4--) {
    let i9 = s99.attributes[e4].name;
    t5[i9] == null && s99.removeAttribute(i9);
  }
  for (let e4 in t5) {
    let i9 = t5[e4];
    e4 == "style" ? s99.style.cssText = i9 : s99.getAttribute(e4) != i9 && s99.setAttribute(e4, i9);
  }
}
function fs(s99, t5, e4) {
  let i9 = false;
  if (t5) for (let n22 in t5) e4 && n22 in e4 || (i9 = true, n22 == "style" ? s99.style.cssText = "" : s99.removeAttribute(n22));
  if (e4) for (let n22 in e4) t5 && t5[n22] == e4[n22] || (i9 = true, n22 == "style" ? s99.style.cssText = e4[n22] : s99.setAttribute(n22, e4[n22]));
  return i9;
}
function co2(s99) {
  let t5 = /* @__PURE__ */ Object.create(null);
  for (let e4 = 0; e4 < s99.attributes.length; e4++) {
    let i9 = s99.attributes[e4];
    t5[i9.name] = i9.value;
  }
  return t5;
}
var et4 = class {
  eq(t5) {
    return false;
  }
  updateDOM(t5, e4) {
    return false;
  }
  compare(t5) {
    return this == t5 || this.constructor == t5.constructor && this.eq(t5);
  }
  get estimatedHeight() {
    return -1;
  }
  get lineBreaks() {
    return 0;
  }
  ignoreEvent(t5) {
    return true;
  }
  coordsAt(t5, e4, i9) {
    return null;
  }
  get isHidden() {
    return false;
  }
  get editable() {
    return false;
  }
  destroy(t5) {
  }
};
var P8 = function(s99) {
  return s99[s99.Text = 0] = "Text", s99[s99.WidgetBefore = 1] = "WidgetBefore", s99[s99.WidgetAfter = 2] = "WidgetAfter", s99[s99.WidgetRange = 3] = "WidgetRange", s99;
}(P8 || (P8 = {}));
var T8 = class extends q7 {
  constructor(t5, e4, i9, n22) {
    super(), this.startSide = t5, this.endSide = e4, this.widget = i9, this.spec = n22;
  }
  get heightRelevant() {
    return false;
  }
  static mark(t5) {
    return new Ut4(t5);
  }
  static widget(t5) {
    let e4 = Math.max(-1e4, Math.min(1e4, t5.side || 0)), i9 = !!t5.block;
    return e4 += i9 && !t5.inlineOrder ? e4 > 0 ? 3e8 : -4e8 : e4 > 0 ? 1e8 : -1e8, new mt4(t5, e4, e4, i9, t5.widget || null, false);
  }
  static replace(t5) {
    let e4 = !!t5.block, i9, n22;
    if (t5.isBlockGap) i9 = -5e8, n22 = 4e8;
    else {
      let { start: o4, end: r2 } = Us2(t5, e4);
      i9 = (o4 ? e4 ? -3e8 : -1 : 5e8) - 1, n22 = (r2 ? e4 ? 2e8 : 1 : -6e8) + 1;
    }
    return new mt4(t5, i9, n22, e4, t5.widget || null, true);
  }
  static line(t5) {
    return new Qt4(t5);
  }
  static set(t5, e4 = false) {
    return T7.of(t5, e4);
  }
  hasHeight() {
    return this.widget ? this.widget.estimatedHeight > -1 : false;
  }
};
T8.none = T7.empty;
var Ut4 = class s65 extends T8 {
  constructor(t5) {
    let { start: e4, end: i9 } = Us2(t5);
    super(e4 ? -1 : 5e8, i9 ? 1 : -6e8, null, t5), this.tagName = t5.tagName || "span", this.attrs = t5.class && t5.attributes ? Zi2(t5.attributes, {
      class: t5.class
    }) : t5.class ? {
      class: t5.class
    } : t5.attributes || Me7;
  }
  eq(t5) {
    return this == t5 || t5 instanceof s65 && this.tagName == t5.tagName && ts2(this.attrs, t5.attrs);
  }
  range(t5, e4 = t5) {
    if (t5 >= e4) throw new RangeError("Mark decorations may not be empty");
    return super.range(t5, e4);
  }
};
Ut4.prototype.point = false;
var Qt4 = class s66 extends T8 {
  constructor(t5) {
    super(-2e8, -2e8, null, t5);
  }
  eq(t5) {
    return t5 instanceof s66 && this.spec.class == t5.spec.class && ts2(this.spec.attributes, t5.spec.attributes);
  }
  range(t5, e4 = t5) {
    if (e4 != t5) throw new RangeError("Line decoration ranges must be zero-length");
    return super.range(t5, e4);
  }
};
Qt4.prototype.mapMode = E6.TrackBefore;
Qt4.prototype.point = true;
var mt4 = class s67 extends T8 {
  constructor(t5, e4, i9, n22, o4, r2) {
    super(e4, i9, o4, t5), this.block = n22, this.isReplace = r2, this.mapMode = n22 ? e4 <= 0 ? E6.TrackBefore : E6.TrackAfter : E6.TrackDel;
  }
  get type() {
    return this.startSide != this.endSide ? P8.WidgetRange : this.startSide <= 0 ? P8.WidgetBefore : P8.WidgetAfter;
  }
  get heightRelevant() {
    return this.block || !!this.widget && (this.widget.estimatedHeight >= 5 || this.widget.lineBreaks > 0);
  }
  eq(t5) {
    return t5 instanceof s67 && fo(this.widget, t5.widget) && this.block == t5.block && this.startSide == t5.startSide && this.endSide == t5.endSide;
  }
  range(t5, e4 = t5) {
    if (this.isReplace && (t5 > e4 || t5 == e4 && this.startSide > 0 && this.endSide <= 0)) throw new RangeError("Invalid range for replacement decoration");
    if (!this.isReplace && e4 != t5) throw new RangeError("Widget decorations can only have zero-length ranges");
    return super.range(t5, e4);
  }
};
mt4.prototype.point = true;
function Us2(s99, t5 = false) {
  let { inclusiveStart: e4, inclusiveEnd: i9 } = s99;
  return e4 == null && (e4 = s99.inclusive), i9 == null && (i9 = s99.inclusive), {
    start: e4 ?? t5,
    end: i9 ?? t5
  };
}
function fo(s99, t5) {
  return s99 == t5 || !!(s99 && t5 && s99.compare(t5));
}
function Tt5(s99, t5, e4, i9 = 0) {
  let n22 = e4.length - 1;
  n22 >= 0 && e4[n22] + i9 >= s99 ? e4[n22] = Math.max(e4[n22], t5) : e4.push(s99, t5);
}
var ke8 = class s68 extends q7 {
  constructor(t5, e4) {
    super(), this.tagName = t5, this.attributes = e4;
  }
  eq(t5) {
    return t5 == this || t5 instanceof s68 && this.tagName == t5.tagName && ts2(this.attributes, t5.attributes);
  }
  static create(t5) {
    return new s68(t5.tagName, t5.attributes || Me7);
  }
  static set(t5, e4 = false) {
    return T7.of(t5, e4);
  }
};
ke8.prototype.startSide = ke8.prototype.endSide = -1;
function Jt3(s99) {
  let t5;
  return s99.nodeType == 11 ? t5 = s99.getSelection ? s99 : s99.ownerDocument : t5 = s99, t5.getSelection();
}
function ni2(s99, t5) {
  return t5 ? s99 == t5 || s99.contains(t5.nodeType != 1 ? t5.parentNode : t5) : false;
}
function be7(s99, t5) {
  if (!t5.anchorNode) return false;
  try {
    return ni2(s99, t5.anchorNode);
  } catch {
    return false;
  }
}
function zt3(s99) {
  return s99.nodeType == 3 ? te8(s99, 0, s99.nodeValue.length).getClientRects() : s99.nodeType == 1 ? s99.getClientRects() : [];
}
function qt3(s99, t5, e4, i9) {
  return e4 ? ds2(s99, t5, e4, i9, -1) || ds2(s99, t5, e4, i9, 1) : false;
}
function ct4(s99) {
  for (var t5 = 0; ; t5++) if (s99 = s99.previousSibling, !s99) return t5;
}
function Ae6(s99) {
  return s99.nodeType == 1 && /^(DIV|P|LI|UL|OL|BLOCKQUOTE|DD|DT|H\d|SECTION|PRE)$/.test(s99.nodeName);
}
function ds2(s99, t5, e4, i9, n22) {
  for (; ; ) {
    if (s99 == e4 && t5 == i9) return true;
    if (t5 == (n22 < 0 ? 0 : it6(s99))) {
      if (s99.nodeName == "DIV") return false;
      let o4 = s99.parentNode;
      if (!o4 || o4.nodeType != 1) return false;
      t5 = ct4(s99) + (n22 < 0 ? 0 : 1), s99 = o4;
    } else if (s99.nodeType == 1) {
      if (s99 = s99.childNodes[t5 + (n22 < 0 ? -1 : 0)], s99.nodeType == 1 && s99.contentEditable == "false") return false;
      t5 = n22 < 0 ? it6(s99) : 0;
    } else return false;
  }
}
function it6(s99) {
  return s99.nodeType == 3 ? s99.nodeValue.length : s99.childNodes.length;
}
function Zt3(s99, t5) {
  let e4 = t5 ? s99.left : s99.right;
  return {
    left: e4,
    right: e4,
    top: s99.top,
    bottom: s99.bottom
  };
}
function uo(s99) {
  let t5 = s99.visualViewport;
  return t5 ? {
    left: 0,
    right: t5.width,
    top: 0,
    bottom: t5.height
  } : {
    left: 0,
    right: s99.innerWidth,
    top: 0,
    bottom: s99.innerHeight
  };
}
function Qs2(s99, t5) {
  let e4 = t5.width / s99.offsetWidth, i9 = t5.height / s99.offsetHeight;
  return (e4 > 0.995 && e4 < 1.005 || !isFinite(e4) || Math.abs(t5.width - s99.offsetWidth) < 1) && (e4 = 1), (i9 > 0.995 && i9 < 1.005 || !isFinite(i9) || Math.abs(t5.height - s99.offsetHeight) < 1) && (i9 = 1), {
    scaleX: e4,
    scaleY: i9
  };
}
function po2(s99, t5, e4, i9, n22, o4, r2, l11) {
  let a2 = s99.ownerDocument, h3 = a2.defaultView || globalThis;
  for (let c4 = s99, f2 = false; c4 && !f2; ) if (c4.nodeType == 1) {
    let d5, u5 = c4 == a2.body, p5 = 1, g6 = 1;
    if (u5) d5 = uo(h3);
    else {
      if (/^(fixed|sticky)$/.test(getComputedStyle(c4).position) && (f2 = true), c4.scrollHeight <= c4.clientHeight && c4.scrollWidth <= c4.clientWidth) {
        c4 = c4.assignedSlot || c4.parentNode;
        continue;
      }
      let w11 = c4.getBoundingClientRect();
      ({ scaleX: p5, scaleY: g6 } = Qs2(c4, w11)), d5 = {
        left: w11.left,
        right: w11.left + c4.clientWidth * p5,
        top: w11.top,
        bottom: w11.top + c4.clientHeight * g6
      };
    }
    let m9 = 0, b9 = 0;
    if (n22 == "nearest") t5.top < d5.top ? (b9 = t5.top - (d5.top + r2), e4 > 0 && t5.bottom > d5.bottom + b9 && (b9 = t5.bottom - d5.bottom + r2)) : t5.bottom > d5.bottom && (b9 = t5.bottom - d5.bottom + r2, e4 < 0 && t5.top - b9 < d5.top && (b9 = t5.top - (d5.top + r2)));
    else {
      let w11 = t5.bottom - t5.top, M14 = d5.bottom - d5.top;
      b9 = (n22 == "center" && w11 <= M14 ? t5.top + w11 / 2 - M14 / 2 : n22 == "start" || n22 == "center" && e4 < 0 ? t5.top - r2 : t5.bottom - M14 + r2) - d5.top;
    }
    if (i9 == "nearest" ? t5.left < d5.left ? (m9 = t5.left - (d5.left + o4), e4 > 0 && t5.right > d5.right + m9 && (m9 = t5.right - d5.right + o4)) : t5.right > d5.right && (m9 = t5.right - d5.right + o4, e4 < 0 && t5.left < d5.left + m9 && (m9 = t5.left - (d5.left + o4))) : m9 = (i9 == "center" ? t5.left + (t5.right - t5.left) / 2 - (d5.right - d5.left) / 2 : i9 == "start" == l11 ? t5.left - o4 : t5.right - (d5.right - d5.left) + o4) - d5.left, m9 || b9) if (u5) h3.scrollBy(m9, b9);
    else {
      let w11 = 0, M14 = 0;
      if (b9) {
        let A11 = c4.scrollTop;
        c4.scrollTop += b9 / g6, M14 = (c4.scrollTop - A11) * g6;
      }
      if (m9) {
        let A11 = c4.scrollLeft;
        c4.scrollLeft += m9 / p5, w11 = (c4.scrollLeft - A11) * p5;
      }
      t5 = {
        left: t5.left - w11,
        top: t5.top - M14,
        right: t5.right - w11,
        bottom: t5.bottom - M14
      }, w11 && Math.abs(w11 - m9) < 1 && (i9 = "nearest"), M14 && Math.abs(M14 - b9) < 1 && (n22 = "nearest");
    }
    if (u5) break;
    (t5.top < d5.top || t5.bottom > d5.bottom || t5.left < d5.left || t5.right > d5.right) && (t5 = {
      left: Math.max(t5.left, d5.left),
      right: Math.min(t5.right, d5.right),
      top: Math.max(t5.top, d5.top),
      bottom: Math.min(t5.bottom, d5.bottom)
    }), c4 = c4.assignedSlot || c4.parentNode;
  } else if (c4.nodeType == 11) c4 = c4.host;
  else break;
}
function go2(s99) {
  let t5 = s99.ownerDocument, e4, i9;
  for (let n22 = s99.parentNode; n22 && !(n22 == t5.body || e4 && i9); ) if (n22.nodeType == 1) !i9 && n22.scrollHeight > n22.clientHeight && (i9 = n22), !e4 && n22.scrollWidth > n22.clientWidth && (e4 = n22), n22 = n22.assignedSlot || n22.parentNode;
  else if (n22.nodeType == 11) n22 = n22.host;
  else break;
  return {
    x: e4,
    y: i9
  };
}
var oi2 = class {
  constructor() {
    this.anchorNode = null, this.anchorOffset = 0, this.focusNode = null, this.focusOffset = 0;
  }
  eq(t5) {
    return this.anchorNode == t5.anchorNode && this.anchorOffset == t5.anchorOffset && this.focusNode == t5.focusNode && this.focusOffset == t5.focusOffset;
  }
  setRange(t5) {
    let { anchorNode: e4, focusNode: i9 } = t5;
    this.set(e4, Math.min(t5.anchorOffset, e4 ? it6(e4) : 0), i9, Math.min(t5.focusOffset, i9 ? it6(i9) : 0));
  }
  set(t5, e4, i9, n22) {
    this.anchorNode = t5, this.anchorOffset = e4, this.focusNode = i9, this.focusOffset = n22;
  }
};
var pt4 = null;
y8.safari && y8.safari_version >= 26 && (pt4 = false);
function Js2(s99) {
  if (s99.setActive) return s99.setActive();
  if (pt4) return s99.focus(pt4);
  let t5 = [];
  for (let e4 = s99; e4 && (t5.push(e4, e4.scrollTop, e4.scrollLeft), e4 != e4.ownerDocument); e4 = e4.parentNode) ;
  if (s99.focus(pt4 == null ? {
    get preventScroll() {
      return pt4 = {
        preventScroll: true
      }, true;
    }
  } : void 0), !pt4) {
    pt4 = false;
    for (let e4 = 0; e4 < t5.length; ) {
      let i9 = t5[e4++], n22 = t5[e4++], o4 = t5[e4++];
      i9.scrollTop != n22 && (i9.scrollTop = n22), i9.scrollLeft != o4 && (i9.scrollLeft = o4);
    }
  }
}
var us2;
function te8(s99, t5, e4 = t5) {
  let i9 = us2 || (us2 = document.createRange());
  return i9.setEnd(s99, e4), i9.setStart(s99, t5), i9;
}
function Dt5(s99, t5, e4, i9) {
  let n22 = {
    key: t5,
    code: t5,
    keyCode: e4,
    which: e4,
    cancelable: true
  };
  i9 && ({ altKey: n22.altKey, ctrlKey: n22.ctrlKey, shiftKey: n22.shiftKey, metaKey: n22.metaKey } = i9);
  let o4 = new KeyboardEvent("keydown", n22);
  o4.synthetic = true, s99.dispatchEvent(o4);
  let r2 = new KeyboardEvent("keyup", n22);
  return r2.synthetic = true, s99.dispatchEvent(r2), o4.defaultPrevented || r2.defaultPrevented;
}
function mo2(s99) {
  for (; s99; ) {
    if (s99 && (s99.nodeType == 9 || s99.nodeType == 11 && s99.host)) return s99;
    s99 = s99.assignedSlot || s99.parentNode;
  }
  return null;
}
function bo2(s99, t5) {
  let e4 = t5.focusNode, i9 = t5.focusOffset;
  if (!e4 || t5.anchorNode != e4 || t5.anchorOffset != i9) return false;
  for (i9 = Math.min(i9, it6(e4)); ; ) if (i9) {
    if (e4.nodeType != 1) return false;
    let n22 = e4.childNodes[i9 - 1];
    n22.contentEditable == "false" ? i9-- : (e4 = n22, i9 = it6(e4));
  } else {
    if (e4 == s99) return true;
    i9 = ct4(e4), e4 = e4.parentNode;
  }
}
function Zs2(s99) {
  return s99.scrollTop > Math.max(1, s99.scrollHeight - s99.clientHeight - 4);
}
function tn3(s99, t5) {
  for (let e4 = s99, i9 = t5; ; ) {
    if (e4.nodeType == 3 && i9 > 0) return {
      node: e4,
      offset: i9
    };
    if (e4.nodeType == 1 && i9 > 0) {
      if (e4.contentEditable == "false") return null;
      e4 = e4.childNodes[i9 - 1], i9 = it6(e4);
    } else if (e4.parentNode && !Ae6(e4)) i9 = ct4(e4), e4 = e4.parentNode;
    else return null;
  }
}
function en3(s99, t5) {
  for (let e4 = s99, i9 = t5; ; ) {
    if (e4.nodeType == 3 && i9 < e4.nodeValue.length) return {
      node: e4,
      offset: i9
    };
    if (e4.nodeType == 1 && i9 < e4.childNodes.length) {
      if (e4.contentEditable == "false") return null;
      e4 = e4.childNodes[i9], i9 = 0;
    } else if (e4.parentNode && !Ae6(e4)) i9 = ct4(e4) + 1, e4 = e4.parentNode;
    else return null;
  }
}
var G7 = class s69 {
  constructor(t5, e4, i9 = true) {
    this.node = t5, this.offset = e4, this.precise = i9;
  }
  static before(t5, e4) {
    return new s69(t5.parentNode, ct4(t5), e4);
  }
  static after(t5, e4) {
    return new s69(t5.parentNode, ct4(t5) + 1, e4);
  }
};
var R9 = function(s99) {
  return s99[s99.LTR = 0] = "LTR", s99[s99.RTL = 1] = "RTL", s99;
}(R9 || (R9 = {}));
var bt4 = R9.LTR;
var es2 = R9.RTL;
function sn4(s99) {
  let t5 = [];
  for (let e4 = 0; e4 < s99.length; e4++) t5.push(1 << +s99[e4]);
  return t5;
}
var yo = sn4("88888888888888888888888888888888888666888888787833333333337888888000000000000000000000000008888880000000000000000000000000088888888888888888888888888888888888887866668888088888663380888308888800000000000000000000000800000000000000000000000000000008");
var wo = sn4("4444448826627288999999999992222222222222222222222222222222222222222222222229999999999999999999994444444444644222822222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222999999949999999229989999223333333333");
var ri2 = /* @__PURE__ */ Object.create(null);
var $7 = [];
for (let s99 of [
  "()",
  "[]",
  "{}"
]) {
  let t5 = s99.charCodeAt(0), e4 = s99.charCodeAt(1);
  ri2[t5] = e4, ri2[e4] = -t5;
}
function nn2(s99) {
  return s99 <= 247 ? yo[s99] : 1424 <= s99 && s99 <= 1524 ? 2 : 1536 <= s99 && s99 <= 1785 ? wo[s99 - 1536] : 1774 <= s99 && s99 <= 2220 ? 4 : 8192 <= s99 && s99 <= 8204 ? 256 : 64336 <= s99 && s99 <= 65023 ? 4 : 1;
}
var xo = /[\u0590-\u05f4\u0600-\u06ff\u0700-\u08ac\ufb50-\ufdff]/;
var j8 = class {
  get dir() {
    return this.level % 2 ? es2 : bt4;
  }
  constructor(t5, e4, i9) {
    this.from = t5, this.to = e4, this.level = i9;
  }
  side(t5, e4) {
    return this.dir == e4 == t5 ? this.to : this.from;
  }
  forward(t5, e4) {
    return t5 == (this.dir == e4);
  }
  static find(t5, e4, i9, n22) {
    let o4 = -1;
    for (let r2 = 0; r2 < t5.length; r2++) {
      let l11 = t5[r2];
      if (l11.from <= e4 && l11.to >= e4) {
        if (l11.level == i9) return r2;
        (o4 < 0 || (n22 != 0 ? n22 < 0 ? l11.from < e4 : l11.to > e4 : t5[o4].level > l11.level)) && (o4 = r2);
      }
    }
    if (o4 < 0) throw new RangeError("Index out of range");
    return o4;
  }
};
function on3(s99, t5) {
  if (s99.length != t5.length) return false;
  for (let e4 = 0; e4 < s99.length; e4++) {
    let i9 = s99[e4], n22 = t5[e4];
    if (i9.from != n22.from || i9.to != n22.to || i9.direction != n22.direction || !on3(i9.inner, n22.inner)) return false;
  }
  return true;
}
var O7 = [];
function vo(s99, t5, e4, i9, n22) {
  for (let o4 = 0; o4 <= i9.length; o4++) {
    let r2 = o4 ? i9[o4 - 1].to : t5, l11 = o4 < i9.length ? i9[o4].from : e4, a2 = o4 ? 256 : n22;
    for (let h3 = r2, c4 = a2, f2 = a2; h3 < l11; h3++) {
      let d5 = nn2(s99.charCodeAt(h3));
      d5 == 512 ? d5 = c4 : d5 == 8 && f2 == 4 && (d5 = 16), O7[h3] = d5 == 4 ? 2 : d5, d5 & 7 && (f2 = d5), c4 = d5;
    }
    for (let h3 = r2, c4 = a2, f2 = a2; h3 < l11; h3++) {
      let d5 = O7[h3];
      if (d5 == 128) h3 < l11 - 1 && c4 == O7[h3 + 1] && c4 & 24 ? d5 = O7[h3] = c4 : O7[h3] = 256;
      else if (d5 == 64) {
        let u5 = h3 + 1;
        for (; u5 < l11 && O7[u5] == 64; ) u5++;
        let p5 = h3 && c4 == 8 || u5 < e4 && O7[u5] == 8 ? f2 == 1 ? 1 : 8 : 256;
        for (let g6 = h3; g6 < u5; g6++) O7[g6] = p5;
        h3 = u5 - 1;
      } else d5 == 8 && f2 == 1 && (O7[h3] = 1);
      c4 = d5, d5 & 7 && (f2 = d5);
    }
  }
}
function So(s99, t5, e4, i9, n22) {
  let o4 = n22 == 1 ? 2 : 1;
  for (let r2 = 0, l11 = 0, a2 = 0; r2 <= i9.length; r2++) {
    let h3 = r2 ? i9[r2 - 1].to : t5, c4 = r2 < i9.length ? i9[r2].from : e4;
    for (let f2 = h3, d5, u5, p5; f2 < c4; f2++) if (u5 = ri2[d5 = s99.charCodeAt(f2)]) if (u5 < 0) {
      for (let g6 = l11 - 3; g6 >= 0; g6 -= 3) if ($7[g6 + 1] == -u5) {
        let m9 = $7[g6 + 2], b9 = m9 & 2 ? n22 : m9 & 4 ? m9 & 1 ? o4 : n22 : 0;
        b9 && (O7[f2] = O7[$7[g6]] = b9), l11 = g6;
        break;
      }
    } else {
      if ($7.length == 189) break;
      $7[l11++] = f2, $7[l11++] = d5, $7[l11++] = a2;
    }
    else if ((p5 = O7[f2]) == 2 || p5 == 1) {
      let g6 = p5 == n22;
      a2 = g6 ? 0 : 1;
      for (let m9 = l11 - 3; m9 >= 0; m9 -= 3) {
        let b9 = $7[m9 + 2];
        if (b9 & 2) break;
        if (g6) $7[m9 + 2] |= 2;
        else {
          if (b9 & 4) break;
          $7[m9 + 2] |= 4;
        }
      }
    }
  }
}
function Co(s99, t5, e4, i9) {
  for (let n22 = 0, o4 = i9; n22 <= e4.length; n22++) {
    let r2 = n22 ? e4[n22 - 1].to : s99, l11 = n22 < e4.length ? e4[n22].from : t5;
    for (let a2 = r2; a2 < l11; ) {
      let h3 = O7[a2];
      if (h3 == 256) {
        let c4 = a2 + 1;
        for (; ; ) if (c4 == l11) {
          if (n22 == e4.length) break;
          c4 = e4[n22++].to, l11 = n22 < e4.length ? e4[n22].from : t5;
        } else if (O7[c4] == 256) c4++;
        else break;
        let f2 = o4 == 1, d5 = (c4 < t5 ? O7[c4] : i9) == 1, u5 = f2 == d5 ? f2 ? 1 : 2 : i9;
        for (let p5 = c4, g6 = n22, m9 = g6 ? e4[g6 - 1].to : s99; p5 > a2; ) p5 == m9 && (p5 = e4[--g6].from, m9 = g6 ? e4[g6 - 1].to : s99), O7[--p5] = u5;
        a2 = c4;
      } else o4 = h3, a2++;
    }
  }
}
function li(s99, t5, e4, i9, n22, o4, r2) {
  let l11 = i9 % 2 ? 2 : 1;
  if (i9 % 2 == n22 % 2) for (let a2 = t5, h3 = 0; a2 < e4; ) {
    let c4 = true, f2 = false;
    if (h3 == o4.length || a2 < o4[h3].from) {
      let g6 = O7[a2];
      g6 != l11 && (c4 = false, f2 = g6 == 16);
    }
    let d5 = !c4 && l11 == 1 ? [] : null, u5 = c4 ? i9 : i9 + 1, p5 = a2;
    t: for (; ; ) if (h3 < o4.length && p5 == o4[h3].from) {
      if (f2) break t;
      let g6 = o4[h3];
      if (!c4) for (let m9 = g6.to, b9 = h3 + 1; ; ) {
        if (m9 == e4) break t;
        if (b9 < o4.length && o4[b9].from == m9) m9 = o4[b9++].to;
        else {
          if (O7[m9] == l11) break t;
          break;
        }
      }
      if (h3++, d5) d5.push(g6);
      else {
        g6.from > a2 && r2.push(new j8(a2, g6.from, u5));
        let m9 = g6.direction == bt4 != !(u5 % 2);
        ai2(s99, m9 ? i9 + 1 : i9, n22, g6.inner, g6.from, g6.to, r2), a2 = g6.to;
      }
      p5 = g6.to;
    } else {
      if (p5 == e4 || (c4 ? O7[p5] != l11 : O7[p5] == l11)) break;
      p5++;
    }
    d5 ? li(s99, a2, p5, i9 + 1, n22, d5, r2) : a2 < p5 && r2.push(new j8(a2, p5, u5)), a2 = p5;
  }
  else for (let a2 = e4, h3 = o4.length; a2 > t5; ) {
    let c4 = true, f2 = false;
    if (!h3 || a2 > o4[h3 - 1].to) {
      let g6 = O7[a2 - 1];
      g6 != l11 && (c4 = false, f2 = g6 == 16);
    }
    let d5 = !c4 && l11 == 1 ? [] : null, u5 = c4 ? i9 : i9 + 1, p5 = a2;
    t: for (; ; ) if (h3 && p5 == o4[h3 - 1].to) {
      if (f2) break t;
      let g6 = o4[--h3];
      if (!c4) for (let m9 = g6.from, b9 = h3; ; ) {
        if (m9 == t5) break t;
        if (b9 && o4[b9 - 1].to == m9) m9 = o4[--b9].from;
        else {
          if (O7[m9 - 1] == l11) break t;
          break;
        }
      }
      if (d5) d5.push(g6);
      else {
        g6.to < a2 && r2.push(new j8(g6.to, a2, u5));
        let m9 = g6.direction == bt4 != !(u5 % 2);
        ai2(s99, m9 ? i9 + 1 : i9, n22, g6.inner, g6.from, g6.to, r2), a2 = g6.from;
      }
      p5 = g6.from;
    } else {
      if (p5 == t5 || (c4 ? O7[p5 - 1] != l11 : O7[p5 - 1] == l11)) break;
      p5--;
    }
    d5 ? li(s99, p5, a2, i9 + 1, n22, d5, r2) : p5 < a2 && r2.push(new j8(p5, a2, u5)), a2 = p5;
  }
}
function ai2(s99, t5, e4, i9, n22, o4, r2) {
  let l11 = t5 % 2 ? 2 : 1;
  vo(s99, n22, o4, i9, l11), So(s99, n22, o4, i9, l11), Co(n22, o4, i9, l11), li(s99, n22, o4, t5, e4, i9, r2);
}
function rn3(s99, t5, e4) {
  if (!s99) return [
    new j8(0, 0, t5 == es2 ? 1 : 0)
  ];
  if (t5 == bt4 && !e4.length && !xo.test(s99)) return ln3(s99.length);
  if (e4.length) for (; s99.length > O7.length; ) O7[O7.length] = 256;
  let i9 = [], n22 = t5 == bt4 ? 0 : 1;
  return ai2(s99, n22, n22, e4, 0, s99.length, i9), i9;
}
function ln3(s99) {
  return [
    new j8(0, s99, 0)
  ];
}
var an3 = "";
function hn3(s99, t5, e4, i9, n22) {
  var o4;
  let r2 = i9.head - s99.from, l11 = j8.find(t5, r2, (o4 = i9.bidiLevel) !== null && o4 !== void 0 ? o4 : -1, i9.assoc), a2 = t5[l11], h3 = a2.side(n22, e4);
  if (r2 == h3) {
    let d5 = l11 += n22 ? 1 : -1;
    if (d5 < 0 || d5 >= t5.length) return null;
    a2 = t5[l11 = d5], r2 = a2.side(!n22, e4), h3 = a2.side(n22, e4);
  }
  let c4 = ee6(s99.text, r2, a2.forward(n22, e4));
  (c4 < a2.from || c4 > a2.to) && (c4 = h3), an3 = s99.text.slice(Math.min(r2, c4), Math.max(r2, c4));
  let f2 = l11 == (n22 ? t5.length - 1 : 0) ? null : t5[l11 + (n22 ? 1 : -1)];
  return f2 && c4 == h3 && f2.level + (n22 ? 0 : 1) < a2.level ? x8.cursor(f2.side(!n22, e4) + s99.from, f2.forward(n22, e4) ? 1 : -1, f2.level) : x8.cursor(c4 + s99.from, a2.forward(n22, e4) ? -1 : 1, a2.level);
}
function Mo(s99, t5, e4) {
  for (let i9 = t5; i9 < e4; i9++) {
    let n22 = nn2(s99.charCodeAt(i9));
    if (n22 == 1) return bt4;
    if (n22 == 2 || n22 == 4) return es2;
  }
  return bt4;
}
var cn2 = k7.define();
var fn = k7.define();
var dn2 = k7.define();
var un2 = k7.define();
var hi2 = k7.define();
var pn = k7.define();
var gn2 = k7.define();
var is2 = k7.define();
var ss2 = k7.define();
var mn = k7.define({
  combine: (s99) => s99.some((t5) => t5)
});
var bn2 = k7.define({
  combine: (s99) => s99.some((t5) => t5)
});
var yn2 = k7.define();
var Kt3 = class s70 {
  constructor(t5, e4 = "nearest", i9 = "nearest", n22 = 5, o4 = 5, r2 = false) {
    this.range = t5, this.y = e4, this.x = i9, this.yMargin = n22, this.xMargin = o4, this.isSnapshot = r2;
  }
  map(t5) {
    return t5.empty ? this : new s70(this.range.map(t5), this.y, this.x, this.yMargin, this.xMargin, this.isSnapshot);
  }
  clip(t5) {
    return this.range.to <= t5.doc.length ? this : new s70(x8.cursor(t5.doc.length), this.y, this.x, this.yMargin, this.xMargin, this.isSnapshot);
  }
};
var ae9 = v5.define({
  map: (s99, t5) => s99.map(t5)
});
var wn2 = v5.define();
function U9(s99, t5, e4) {
  let i9 = s99.facet(un2);
  i9.length ? i9[0](t5) : globalThis.onerror && globalThis.onerror(String(t5), e4, void 0, void 0, t5) || (e4 ? console.error(e4 + ":", t5) : console.error(t5));
}
var tt6 = k7.define({
  combine: (s99) => s99.length ? s99[0] : true
});
var ko = 0;
var St4 = k7.define({
  combine(s99) {
    return s99.filter((t5, e4) => {
      for (let i9 = 0; i9 < e4; i9++) if (s99[i9].plugin == t5.plugin) return false;
      return true;
    });
  }
});
var N10 = class s71 {
  constructor(t5, e4, i9, n22, o4) {
    this.id = t5, this.create = e4, this.domEventHandlers = i9, this.domEventObservers = n22, this.baseExtensions = o4(this), this.extension = this.baseExtensions.concat(St4.of({
      plugin: this,
      arg: void 0
    }));
  }
  of(t5) {
    return this.baseExtensions.concat(St4.of({
      plugin: this,
      arg: t5
    }));
  }
  static define(t5, e4) {
    let { eventHandlers: i9, eventObservers: n22, provide: o4, decorations: r2 } = e4 || {};
    return new s71(ko++, t5, i9, n22, (l11) => {
      let a2 = [];
      return r2 && a2.push(Ke5.of((h3) => {
        let c4 = h3.plugin(l11);
        return c4 ? r2(c4) : T8.none;
      })), o4 && a2.push(o4(l11)), a2;
    });
  }
  static fromClass(t5, e4) {
    return s71.define((i9, n22) => new t5(i9, n22), e4);
  }
};
var _t3 = class {
  constructor(t5) {
    this.spec = t5, this.mustUpdate = null, this.value = null;
  }
  get plugin() {
    return this.spec && this.spec.plugin;
  }
  update(t5) {
    if (this.value) {
      if (this.mustUpdate) {
        let e4 = this.mustUpdate;
        if (this.mustUpdate = null, this.value.update) try {
          this.value.update(e4);
        } catch (i9) {
          if (U9(e4.state, i9, "CodeMirror plugin crashed"), this.value.destroy) try {
            this.value.destroy();
          } catch {
          }
          this.deactivate();
        }
      }
    } else if (this.spec) try {
      this.value = this.spec.plugin.create(t5, this.spec.arg);
    } catch (e4) {
      U9(t5.state, e4, "CodeMirror plugin crashed"), this.deactivate();
    }
    return this;
  }
  destroy(t5) {
    var e4;
    if (!((e4 = this.value) === null || e4 === void 0) && e4.destroy) try {
      this.value.destroy();
    } catch (i9) {
      U9(t5.state, i9, "CodeMirror plugin crashed");
    }
  }
  deactivate() {
    this.spec = this.value = null;
  }
};
var xn2 = k7.define();
var qe6 = k7.define();
var Ke5 = k7.define();
var vn2 = k7.define();
var ns2 = k7.define();
var ne8 = k7.define();
var Sn2 = k7.define();
function ps2(s99, t5) {
  let e4 = s99.state.facet(Sn2);
  if (!e4.length) return e4;
  let i9 = e4.map((o4) => o4 instanceof Function ? o4(s99) : o4), n22 = [];
  return T7.spans(i9, t5.from, t5.to, {
    point() {
    },
    span(o4, r2, l11, a2) {
      let h3 = o4 - t5.from, c4 = r2 - t5.from, f2 = n22;
      for (let d5 = l11.length - 1; d5 >= 0; d5--, a2--) {
        let u5 = l11[d5].spec.bidiIsolate, p5;
        if (u5 == null && (u5 = Mo(t5.text, h3, c4)), a2 > 0 && f2.length && (p5 = f2[f2.length - 1]).to == h3 && p5.direction == u5) p5.to = c4, f2 = p5.inner;
        else {
          let g6 = {
            from: h3,
            to: c4,
            direction: u5,
            inner: []
          };
          f2.push(g6), f2 = g6.inner;
        }
      }
    }
  }), n22;
}
var Cn2 = k7.define();
function os2(s99) {
  let t5 = 0, e4 = 0, i9 = 0, n22 = 0;
  for (let o4 of s99.state.facet(Cn2)) {
    let r2 = o4(s99);
    r2 && (r2.left != null && (t5 = Math.max(t5, r2.left)), r2.right != null && (e4 = Math.max(e4, r2.right)), r2.top != null && (i9 = Math.max(i9, r2.top)), r2.bottom != null && (n22 = Math.max(n22, r2.bottom)));
  }
  return {
    left: t5,
    right: e4,
    top: i9,
    bottom: n22
  };
}
var Nt4 = k7.define();
var q8 = class s72 {
  constructor(t5, e4, i9, n22) {
    this.fromA = t5, this.toA = e4, this.fromB = i9, this.toB = n22;
  }
  join(t5) {
    return new s72(Math.min(this.fromA, t5.fromA), Math.max(this.toA, t5.toA), Math.min(this.fromB, t5.fromB), Math.max(this.toB, t5.toB));
  }
  addToSet(t5) {
    let e4 = t5.length, i9 = this;
    for (; e4 > 0; e4--) {
      let n22 = t5[e4 - 1];
      if (!(n22.fromA > i9.toA)) {
        if (n22.toA < i9.fromA) break;
        i9 = i9.join(n22), t5.splice(e4 - 1, 1);
      }
    }
    return t5.splice(e4, 0, i9), t5;
  }
  static extendWithRanges(t5, e4) {
    if (e4.length == 0) return t5;
    let i9 = [];
    for (let n22 = 0, o4 = 0, r2 = 0; ; ) {
      let l11 = n22 < t5.length ? t5[n22].fromB : 1e9, a2 = o4 < e4.length ? e4[o4] : 1e9, h3 = Math.min(l11, a2);
      if (h3 == 1e9) break;
      let c4 = h3 + r2, f2 = h3, d5 = c4;
      for (; ; ) if (o4 < e4.length && e4[o4] <= f2) {
        let u5 = e4[o4 + 1];
        o4 += 2, f2 = Math.max(f2, u5);
        for (let p5 = n22; p5 < t5.length && t5[p5].fromB <= f2; p5++) r2 = t5[p5].toA - t5[p5].toB;
        d5 = Math.max(d5, u5 + r2);
      } else if (n22 < t5.length && t5[n22].fromB <= f2) {
        let u5 = t5[n22++];
        f2 = Math.max(f2, u5.toB), d5 = Math.max(d5, u5.toA), r2 = u5.toA - u5.toB;
      } else break;
      i9.push(new s72(c4, d5, h3, f2));
    }
    return i9;
  }
};
var Te8 = class s73 {
  constructor(t5, e4, i9) {
    this.view = t5, this.state = e4, this.transactions = i9, this.flags = 0, this.startState = t5.state, this.changes = A8.empty(this.startState.doc.length);
    for (let o4 of i9) this.changes = this.changes.compose(o4.changes);
    let n22 = [];
    this.changes.iterChangedRanges((o4, r2, l11, a2) => n22.push(new q8(o4, r2, l11, a2))), this.changedRanges = n22;
  }
  static create(t5, e4, i9) {
    return new s73(t5, e4, i9);
  }
  get viewportChanged() {
    return (this.flags & 4) > 0;
  }
  get viewportMoved() {
    return (this.flags & 8) > 0;
  }
  get heightChanged() {
    return (this.flags & 2) > 0;
  }
  get geometryChanged() {
    return this.docChanged || (this.flags & 18) > 0;
  }
  get focusChanged() {
    return (this.flags & 1) > 0;
  }
  get docChanged() {
    return !this.changes.empty;
  }
  get selectionSet() {
    return this.transactions.some((t5) => t5.selection);
  }
  get empty() {
    return this.flags == 0 && this.transactions.length == 0;
  }
};
var Ao = [];
var B9 = class {
  constructor(t5, e4, i9 = 0) {
    this.dom = t5, this.length = e4, this.flags = i9, this.parent = null, t5.cmTile = this;
  }
  get breakAfter() {
    return this.flags & 1;
  }
  get children() {
    return Ao;
  }
  isWidget() {
    return false;
  }
  get isHidden() {
    return false;
  }
  isComposite() {
    return false;
  }
  isLine() {
    return false;
  }
  isText() {
    return false;
  }
  isBlock() {
    return false;
  }
  get domAttrs() {
    return null;
  }
  sync(t5) {
    if (this.flags |= 2, this.flags & 4) {
      this.flags &= -5;
      let e4 = this.domAttrs;
      e4 && ho2(this.dom, e4);
    }
  }
  toString() {
    return this.constructor.name + (this.children.length ? `(${this.children})` : "") + (this.breakAfter ? "#" : "");
  }
  destroy() {
    this.parent = null;
  }
  setDOM(t5) {
    this.dom = t5, t5.cmTile = this;
  }
  get posAtStart() {
    return this.parent ? this.parent.posBefore(this) : 0;
  }
  get posAtEnd() {
    return this.posAtStart + this.length;
  }
  posBefore(t5, e4 = this.posAtStart) {
    let i9 = e4;
    for (let n22 of this.children) {
      if (n22 == t5) return i9;
      i9 += n22.length + n22.breakAfter;
    }
    throw new RangeError("Invalid child in posBefore");
  }
  posAfter(t5) {
    return this.posBefore(t5) + t5.length;
  }
  covers(t5) {
    return true;
  }
  coordsIn(t5, e4) {
    return null;
  }
  domPosFor(t5, e4) {
    let i9 = ct4(this.dom), n22 = this.length ? t5 > 0 : e4 > 0;
    return new G7(this.parent.dom, i9 + (n22 ? 1 : 0), t5 == 0 || t5 == this.length);
  }
  markDirty(t5) {
    this.flags &= -3, t5 && (this.flags |= 4), this.parent && this.parent.flags & 2 && this.parent.markDirty(false);
  }
  get overrideDOMText() {
    return null;
  }
  get root() {
    for (let t5 = this; t5; t5 = t5.parent) if (t5 instanceof Rt4) return t5;
    return null;
  }
  static get(t5) {
    return t5.cmTile;
  }
};
var Lt5 = class extends B9 {
  constructor(t5) {
    super(t5, 0), this._children = [];
  }
  isComposite() {
    return true;
  }
  get children() {
    return this._children;
  }
  get lastChild() {
    return this.children.length ? this.children[this.children.length - 1] : null;
  }
  append(t5) {
    this.children.push(t5), t5.parent = this;
  }
  sync(t5) {
    if (this.flags & 2) return;
    super.sync(t5);
    let e4 = this.dom, i9 = null, n22, o4 = t5?.node == e4 ? t5 : null, r2 = 0;
    for (let l11 of this.children) {
      if (l11.sync(t5), r2 += l11.length + l11.breakAfter, n22 = i9 ? i9.nextSibling : e4.firstChild, o4 && n22 != l11.dom && (o4.written = true), l11.dom.parentNode == e4) for (; n22 && n22 != l11.dom; ) n22 = gs2(n22);
      else e4.insertBefore(l11.dom, n22);
      i9 = l11.dom;
    }
    for (n22 = i9 ? i9.nextSibling : e4.firstChild, o4 && n22 && (o4.written = true); n22; ) n22 = gs2(n22);
    this.length = r2;
  }
};
function gs2(s99) {
  let t5 = s99.nextSibling;
  return s99.parentNode.removeChild(s99), t5;
}
var Rt4 = class extends Lt5 {
  constructor(t5, e4) {
    super(e4), this.view = t5;
  }
  owns(t5) {
    for (; t5; t5 = t5.parent) if (t5 == this) return true;
    return false;
  }
  isBlock() {
    return true;
  }
  nearest(t5) {
    for (; ; ) {
      if (!t5) return null;
      let e4 = B9.get(t5);
      if (e4 && this.owns(e4)) return e4;
      t5 = t5.parentNode;
    }
  }
  blockTiles(t5) {
    for (let e4 = [], i9 = this, n22 = 0, o4 = 0; ; ) if (n22 == i9.children.length) {
      if (!e4.length) return;
      i9 = i9.parent, i9.breakAfter && o4++, n22 = e4.pop();
    } else {
      let r2 = i9.children[n22++];
      if (r2 instanceof at6) e4.push(n22), i9 = r2, n22 = 0;
      else {
        let l11 = o4 + r2.length, a2 = t5(r2, o4);
        if (a2 !== void 0) return a2;
        o4 = l11 + r2.breakAfter;
      }
    }
  }
  resolveBlock(t5, e4) {
    let i9, n22 = -1, o4, r2 = -1;
    if (this.blockTiles((l11, a2) => {
      let h3 = a2 + l11.length;
      if (t5 >= a2 && t5 <= h3) {
        if (l11.isWidget() && e4 >= -1 && e4 <= 1) {
          if (l11.flags & 32) return true;
          l11.flags & 16 && (i9 = void 0);
        }
        (a2 < t5 || t5 == h3 && (e4 < -1 ? l11.length : l11.covers(1))) && (!i9 || !l11.isWidget() && i9.isWidget()) && (i9 = l11, n22 = t5 - a2), (h3 > t5 || t5 == a2 && (e4 > 1 ? l11.length : l11.covers(-1))) && (!o4 || !l11.isWidget() && o4.isWidget()) && (o4 = l11, r2 = t5 - a2);
      }
    }), !i9 && !o4) throw new Error("No tile at position " + t5);
    return i9 && e4 < 0 || !o4 ? {
      tile: i9,
      offset: n22
    } : {
      tile: o4,
      offset: r2
    };
  }
};
var at6 = class s74 extends Lt5 {
  constructor(t5, e4) {
    super(t5), this.wrapper = e4;
  }
  isBlock() {
    return true;
  }
  covers(t5) {
    return this.children.length ? t5 < 0 ? this.children[0].covers(-1) : this.lastChild.covers(1) : false;
  }
  get domAttrs() {
    return this.wrapper.attributes;
  }
  static of(t5, e4) {
    let i9 = new s74(e4 || document.createElement(t5.tagName), t5);
    return e4 || (i9.flags |= 4), i9;
  }
};
var Bt5 = class s75 extends Lt5 {
  constructor(t5, e4) {
    super(t5), this.attrs = e4;
  }
  isLine() {
    return true;
  }
  static start(t5, e4, i9) {
    let n22 = new s75(e4 || document.createElement("div"), t5);
    return (!e4 || !i9) && (n22.flags |= 4), n22;
  }
  get domAttrs() {
    return this.attrs;
  }
  resolveInline(t5, e4, i9) {
    let n22 = null, o4 = -1, r2 = null, l11 = -1;
    function a2(c4, f2) {
      for (let d5 = 0, u5 = 0; d5 < c4.children.length && u5 <= f2; d5++) {
        let p5 = c4.children[d5], g6 = u5 + p5.length;
        g6 >= f2 && (p5.isComposite() ? a2(p5, f2 - u5) : (!r2 || r2.isHidden && (e4 > 0 || i9 && Do(r2, p5))) && (g6 > f2 || p5.flags & 32) ? (r2 = p5, l11 = f2 - u5) : (u5 < f2 || p5.flags & 16 && !p5.isHidden) && (n22 = p5, o4 = f2 - u5)), u5 = g6;
      }
    }
    a2(this, t5);
    let h3 = (e4 < 0 ? n22 : r2) || n22 || r2;
    return h3 ? {
      tile: h3,
      offset: h3 == n22 ? o4 : l11
    } : null;
  }
  coordsIn(t5, e4) {
    let i9 = this.resolveInline(t5, e4, true);
    return i9 ? i9.tile.coordsIn(Math.max(0, i9.offset), e4) : To(this);
  }
  domIn(t5, e4) {
    let i9 = this.resolveInline(t5, e4);
    if (i9) {
      let { tile: n22, offset: o4 } = i9;
      if (this.dom.contains(n22.dom)) return n22.isText() ? new G7(n22.dom, Math.min(n22.dom.nodeValue.length, o4)) : n22.domPosFor(o4, n22.flags & 16 ? 1 : n22.flags & 32 ? -1 : e4);
      let r2 = i9.tile.parent, l11 = false;
      for (let a2 of r2.children) {
        if (l11) return new G7(a2.dom, 0);
        a2 == i9.tile && (l11 = true);
      }
    }
    return new G7(this.dom, 0);
  }
};
function To(s99) {
  let t5 = s99.dom.lastChild;
  if (!t5) return s99.dom.getBoundingClientRect();
  let e4 = zt3(t5);
  return e4[e4.length - 1] || null;
}
function Do(s99, t5) {
  let e4 = s99.coordsIn(0, 1), i9 = t5.coordsIn(0, 1);
  return e4 && i9 && i9.top < e4.bottom;
}
var V10 = class s76 extends Lt5 {
  constructor(t5, e4) {
    super(t5), this.mark = e4;
  }
  get domAttrs() {
    return this.mark.attrs;
  }
  static of(t5, e4) {
    let i9 = new s76(e4 || document.createElement(t5.tagName), t5);
    return e4 || (i9.flags |= 4), i9;
  }
};
var gt3 = class s77 extends B9 {
  constructor(t5, e4) {
    super(t5, e4.length), this.text = e4;
  }
  sync(t5) {
    this.flags & 2 || (super.sync(t5), this.dom.nodeValue != this.text && (t5 && t5.node == this.dom && (t5.written = true), this.dom.nodeValue = this.text));
  }
  isText() {
    return true;
  }
  toString() {
    return JSON.stringify(this.text);
  }
  coordsIn(t5, e4) {
    let i9 = this.dom.nodeValue.length;
    t5 > i9 && (t5 = i9);
    let n22 = t5, o4 = t5, r2 = 0;
    t5 == 0 && e4 < 0 || t5 == i9 && e4 >= 0 ? y8.chrome || y8.gecko || (t5 ? (n22--, r2 = 1) : o4 < i9 && (o4++, r2 = -1)) : e4 < 0 ? n22-- : o4 < i9 && o4++;
    let l11 = te8(this.dom, n22, o4).getClientRects();
    if (!l11.length) return null;
    let a2 = l11[(r2 ? r2 < 0 : e4 >= 0) ? 0 : l11.length - 1];
    return y8.safari && !r2 && a2.width == 0 && (a2 = Array.prototype.find.call(l11, (h3) => h3.width) || a2), r2 ? Zt3(a2, r2 < 0) : a2 || null;
  }
  static of(t5, e4) {
    let i9 = new s77(e4 || document.createTextNode(t5), t5);
    return e4 || (i9.flags |= 2), i9;
  }
};
var yt4 = class s78 extends B9 {
  constructor(t5, e4, i9, n22) {
    super(t5, e4, n22), this.widget = i9;
  }
  isWidget() {
    return true;
  }
  get isHidden() {
    return this.widget.isHidden;
  }
  covers(t5) {
    return this.flags & 48 ? false : (this.flags & (t5 < 0 ? 64 : 128)) > 0;
  }
  coordsIn(t5, e4) {
    return this.coordsInWidget(t5, e4, false);
  }
  coordsInWidget(t5, e4, i9) {
    let n22 = this.widget.coordsAt(this.dom, t5, e4);
    if (n22) return n22;
    if (i9) return Zt3(this.dom.getBoundingClientRect(), this.length ? t5 == 0 : e4 <= 0);
    {
      let o4 = this.dom.getClientRects(), r2 = null;
      if (!o4.length) return null;
      let l11 = this.flags & 16 ? true : this.flags & 32 ? false : t5 > 0;
      for (let a2 = l11 ? o4.length - 1 : 0; r2 = o4[a2], !(t5 > 0 ? a2 == 0 : a2 == o4.length - 1 || r2.top < r2.bottom); a2 += l11 ? -1 : 1) ;
      return Zt3(r2, !l11);
    }
  }
  get overrideDOMText() {
    if (!this.length) return m7.empty;
    let { root: t5 } = this;
    if (!t5) return m7.empty;
    let e4 = this.posAtStart;
    return t5.view.state.doc.slice(e4, e4 + this.length);
  }
  destroy() {
    super.destroy(), this.widget.destroy(this.dom);
  }
  static of(t5, e4, i9, n22, o4) {
    return o4 || (o4 = t5.toDOM(e4), t5.editable || (o4.contentEditable = "false")), new s78(o4, i9, t5, n22);
  }
};
var Et4 = class extends B9 {
  constructor(t5) {
    let e4 = document.createElement("img");
    e4.className = "cm-widgetBuffer", e4.setAttribute("aria-hidden", "true"), super(e4, 0, t5);
  }
  get isHidden() {
    return true;
  }
  get overrideDOMText() {
    return m7.empty;
  }
  coordsIn(t5) {
    return this.dom.getBoundingClientRect();
  }
};
var ci2 = class {
  constructor(t5) {
    this.index = 0, this.beforeBreak = false, this.parents = [], this.tile = t5;
  }
  advance(t5, e4, i9) {
    let { tile: n22, index: o4, beforeBreak: r2, parents: l11 } = this;
    for (; t5 || e4 > 0; ) if (n22.isComposite()) if (r2) {
      if (!t5) break;
      i9 && i9.break(), t5--, r2 = false;
    } else if (o4 == n22.children.length) {
      if (!t5 && !l11.length) break;
      i9 && i9.leave(n22), r2 = !!n22.breakAfter, { tile: n22, index: o4 } = l11.pop(), o4++;
    } else {
      let a2 = n22.children[o4], h3 = a2.breakAfter;
      (e4 > 0 ? a2.length <= t5 : a2.length < t5) && (!i9 || i9.skip(a2, 0, a2.length) !== false || !a2.isComposite) ? (r2 = !!h3, o4++, t5 -= a2.length) : (l11.push({
        tile: n22,
        index: o4
      }), n22 = a2, o4 = 0, i9 && a2.isComposite() && i9.enter(a2));
    }
    else if (o4 == n22.length) r2 = !!n22.breakAfter, { tile: n22, index: o4 } = l11.pop(), o4++;
    else if (t5) {
      let a2 = Math.min(t5, n22.length - o4);
      i9 && i9.skip(n22, o4, o4 + a2), t5 -= a2, o4 += a2;
    } else break;
    return this.tile = n22, this.index = o4, this.beforeBreak = r2, this;
  }
  get root() {
    return this.parents.length ? this.parents[0].tile : this.tile;
  }
};
var fi2 = class {
  constructor(t5, e4, i9, n22) {
    this.from = t5, this.to = e4, this.wrapper = i9, this.rank = n22;
  }
};
var di2 = class {
  constructor(t5, e4, i9) {
    this.cache = t5, this.root = e4, this.blockWrappers = i9, this.curLine = null, this.lastBlock = null, this.afterWidget = null, this.pos = 0, this.wrappers = [], this.wrapperPos = 0;
  }
  addText(t5, e4, i9, n22) {
    var o4;
    this.flushBuffer();
    let r2 = this.ensureMarks(e4, i9), l11 = r2.lastChild;
    if (l11 && l11.isText() && !(l11.flags & 8)) {
      this.cache.reused.set(l11, 2);
      let a2 = r2.children[r2.children.length - 1] = new gt3(l11.dom, l11.text + t5);
      a2.parent = r2;
    } else r2.append(n22 || gt3.of(t5, (o4 = this.cache.find(gt3)) === null || o4 === void 0 ? void 0 : o4.dom));
    this.pos += t5.length, this.afterWidget = null;
  }
  addComposition(t5, e4) {
    let i9 = this.curLine;
    i9.dom != e4.line.dom && (i9.setDOM(this.cache.reused.has(e4.line) ? Xe6(e4.line.dom) : e4.line.dom), this.cache.reused.set(e4.line, 2));
    let n22 = i9;
    for (let l11 = e4.marks.length - 1; l11 >= 0; l11--) {
      let a2 = e4.marks[l11], h3 = n22.lastChild;
      if (h3 instanceof V10 && h3.mark.eq(a2.mark)) h3.dom != a2.dom && h3.setDOM(Xe6(a2.dom)), n22 = h3;
      else {
        if (this.cache.reused.get(a2)) {
          let f2 = B9.get(a2.dom);
          f2 && f2.setDOM(Xe6(a2.dom));
        }
        let c4 = V10.of(a2.mark, a2.dom);
        n22.append(c4), n22 = c4;
      }
      this.cache.reused.set(a2, 2);
    }
    let o4 = B9.get(t5.text);
    o4 && this.cache.reused.set(o4, 2);
    let r2 = new gt3(t5.text, t5.text.nodeValue);
    r2.flags |= 8, n22.append(r2);
  }
  addInlineWidget(t5, e4, i9) {
    let n22 = this.afterWidget && t5.flags & 48 && (this.afterWidget.flags & 48) == (t5.flags & 48);
    n22 || this.flushBuffer();
    let o4 = this.ensureMarks(e4, i9);
    !n22 && !(t5.flags & 16) && o4.append(this.getBuffer(1)), o4.append(t5), this.pos += t5.length, this.afterWidget = t5;
  }
  addMark(t5, e4, i9) {
    this.flushBuffer(), this.ensureMarks(e4, i9).append(t5), this.pos += t5.length, this.afterWidget = null;
  }
  addBlockWidget(t5) {
    this.getBlockPos().append(t5), this.pos += t5.length, this.lastBlock = t5, this.endLine();
  }
  continueWidget(t5) {
    let e4 = this.afterWidget || this.lastBlock;
    e4.length += t5, this.pos += t5;
  }
  addLineStart(t5, e4) {
    var i9;
    t5 || (t5 = Mn2);
    let n22 = Bt5.start(t5, e4 || ((i9 = this.cache.find(Bt5)) === null || i9 === void 0 ? void 0 : i9.dom), !!e4);
    this.getBlockPos().append(this.lastBlock = this.curLine = n22);
  }
  addLine(t5) {
    this.getBlockPos().append(t5), this.pos += t5.length, this.lastBlock = t5, this.endLine();
  }
  addBreak() {
    this.lastBlock.flags |= 1, this.endLine(), this.pos++;
  }
  addLineStartIfNotCovered(t5) {
    this.blockPosCovered() || this.addLineStart(t5);
  }
  ensureLine(t5) {
    this.curLine || this.addLineStart(t5);
  }
  ensureMarks(t5, e4) {
    var i9;
    let n22 = this.curLine;
    for (let o4 = t5.length - 1; o4 >= 0; o4--) {
      let r2 = t5[o4], l11;
      if (e4 > 0 && (l11 = n22.lastChild) && l11 instanceof V10 && l11.mark.eq(r2)) n22 = l11, e4--;
      else {
        let a2 = V10.of(r2, (i9 = this.cache.find(V10, (h3) => h3.mark.eq(r2))) === null || i9 === void 0 ? void 0 : i9.dom);
        n22.append(a2), n22 = a2, e4 = 0;
      }
    }
    return n22;
  }
  endLine() {
    if (this.curLine) {
      this.flushBuffer();
      let t5 = this.curLine.lastChild;
      (!t5 || !ms2(this.curLine, false) || t5.dom.nodeName != "BR" && t5.isWidget() && !(y8.ios && ms2(this.curLine, true))) && this.curLine.append(this.cache.findWidget($e4, 0, 32) || new yt4($e4.toDOM(), 0, $e4, 32)), this.curLine = this.afterWidget = null;
    }
  }
  updateBlockWrappers() {
    this.wrapperPos > this.pos + 1e4 && (this.blockWrappers.goto(this.pos), this.wrappers.length = 0);
    for (let t5 = this.wrappers.length - 1; t5 >= 0; t5--) this.wrappers[t5].to < this.pos && this.wrappers.splice(t5, 1);
    for (let t5 = this.blockWrappers; t5.value && t5.from <= this.pos; t5.next()) if (t5.to >= this.pos) {
      let e4 = new fi2(t5.from, t5.to, t5.value, t5.rank), i9 = this.wrappers.length;
      for (; i9 > 0 && (this.wrappers[i9 - 1].rank - e4.rank || this.wrappers[i9 - 1].to - e4.to) < 0; ) i9--;
      this.wrappers.splice(i9, 0, e4);
    }
    this.wrapperPos = this.pos;
  }
  getBlockPos() {
    var t5;
    this.updateBlockWrappers();
    let e4 = this.root;
    for (let i9 of this.wrappers) {
      let n22 = e4.lastChild;
      if (i9.from < this.pos && n22 instanceof at6 && n22.wrapper.eq(i9.wrapper)) e4 = n22;
      else {
        let o4 = at6.of(i9.wrapper, (t5 = this.cache.find(at6, (r2) => r2.wrapper.eq(i9.wrapper))) === null || t5 === void 0 ? void 0 : t5.dom);
        e4.append(o4), e4 = o4;
      }
    }
    return e4;
  }
  blockPosCovered() {
    let t5 = this.lastBlock;
    return t5 != null && !t5.breakAfter && (!t5.isWidget() || (t5.flags & 160) > 0);
  }
  getBuffer(t5) {
    let e4 = 2 | (t5 < 0 ? 16 : 32), i9 = this.cache.find(Et4, void 0, 1);
    return i9 && (i9.flags = e4), i9 || new Et4(e4);
  }
  flushBuffer() {
    this.afterWidget && !(this.afterWidget.flags & 32) && (this.afterWidget.parent.append(this.getBuffer(-1)), this.afterWidget = null);
  }
};
var ui2 = class {
  constructor(t5) {
    this.skipCount = 0, this.text = "", this.textOff = 0, this.cursor = t5.iter();
  }
  skip(t5) {
    this.textOff + t5 <= this.text.length ? this.textOff += t5 : (this.skipCount += t5 - (this.text.length - this.textOff), this.text = "", this.textOff = 0);
  }
  next(t5) {
    if (this.textOff == this.text.length) {
      let { value: n22, lineBreak: o4, done: r2 } = this.cursor.next(this.skipCount);
      if (this.skipCount = 0, r2) throw new Error("Ran out of text content when drawing inline views");
      this.text = n22;
      let l11 = this.textOff = Math.min(t5, n22.length);
      return o4 ? null : n22.slice(0, l11);
    }
    let e4 = Math.min(this.text.length, this.textOff + t5), i9 = this.text.slice(this.textOff, e4);
    return this.textOff = e4, i9;
  }
};
var De8 = [
  yt4,
  Bt5,
  gt3,
  V10,
  Et4,
  at6,
  Rt4
];
for (let s99 = 0; s99 < De8.length; s99++) De8[s99].bucket = s99;
var pi = class {
  constructor(t5) {
    this.view = t5, this.buckets = De8.map(() => []), this.index = De8.map(() => 0), this.reused = /* @__PURE__ */ new Map();
  }
  add(t5) {
    let e4 = t5.constructor.bucket, i9 = this.buckets[e4];
    i9.length < 6 ? i9.push(t5) : i9[this.index[e4] = (this.index[e4] + 1) % 6] = t5;
  }
  find(t5, e4, i9 = 2) {
    let n22 = t5.bucket, o4 = this.buckets[n22], r2 = this.index[n22];
    for (let l11 = o4.length - 1; l11 >= 0; l11--) {
      let a2 = (l11 + r2) % o4.length, h3 = o4[a2];
      if ((!e4 || e4(h3)) && !this.reused.has(h3)) return o4.splice(a2, 1), a2 < r2 && this.index[n22]--, this.reused.set(h3, i9), h3;
    }
    return null;
  }
  findWidget(t5, e4, i9) {
    let n22 = this.buckets[0];
    if (n22.length) for (let o4 = 0, r2 = 0; ; o4++) {
      if (o4 == n22.length) {
        if (r2) return null;
        r2 = 1, o4 = 0;
      }
      let l11 = n22[o4];
      if (!this.reused.has(l11) && (r2 == 0 ? l11.widget.compare(t5) : l11.widget.constructor == t5.constructor && t5.updateDOM(l11.dom, this.view))) return n22.splice(o4, 1), o4 < this.index[0] && this.index[0]--, l11.widget == t5 && l11.length == e4 && (l11.flags & 497) == i9 ? (this.reused.set(l11, 1), l11) : (this.reused.set(l11, 2), new yt4(l11.dom, e4, t5, l11.flags & -498 | i9));
    }
  }
  reuse(t5) {
    return this.reused.set(t5, 1), t5;
  }
  maybeReuse(t5, e4 = 2) {
    if (!this.reused.has(t5)) return this.reused.set(t5, e4), t5.dom;
  }
  clear() {
    for (let t5 = 0; t5 < this.buckets.length; t5++) this.buckets[t5].length = this.index[t5] = 0;
  }
};
var gi2 = class {
  constructor(t5, e4, i9, n22, o4) {
    this.view = t5, this.decorations = n22, this.disallowBlockEffectsFor = o4, this.openWidget = false, this.openMarks = 0, this.cache = new pi(t5), this.text = new ui2(t5.state.doc), this.builder = new di2(this.cache, new Rt4(t5, t5.contentDOM), T7.iter(i9)), this.cache.reused.set(e4, 2), this.old = new ci2(e4), this.reuseWalker = {
      skip: (r2, l11, a2) => {
        if (this.cache.add(r2), r2.isComposite()) return false;
      },
      enter: (r2) => this.cache.add(r2),
      leave: () => {
      },
      break: () => {
      }
    };
  }
  run(t5, e4) {
    let i9 = e4 && this.getCompositionContext(e4.text);
    for (let n22 = 0, o4 = 0, r2 = 0; ; ) {
      let l11 = r2 < t5.length ? t5[r2++] : null, a2 = l11 ? l11.fromA : this.old.root.length;
      if (a2 > n22) {
        let h3 = a2 - n22;
        this.preserve(h3, !r2, !l11), n22 = a2, o4 += h3;
      }
      if (!l11) break;
      e4 && l11.fromA <= e4.range.fromA && l11.toA >= e4.range.toA ? (this.forward(l11.fromA, e4.range.fromA, e4.range.fromA < e4.range.toA ? 1 : -1), this.emit(o4, e4.range.fromB), this.cache.clear(), this.builder.addComposition(e4, i9), this.text.skip(e4.range.toB - e4.range.fromB), this.forward(e4.range.fromA, l11.toA), this.emit(e4.range.toB, l11.toB)) : (this.forward(l11.fromA, l11.toA), this.emit(o4, l11.toB)), o4 = l11.toB, n22 = l11.toA;
    }
    return this.builder.curLine && this.builder.endLine(), this.builder.root;
  }
  preserve(t5, e4, i9) {
    let n22 = Ro(this.old), o4 = this.openMarks;
    this.old.advance(t5, i9 ? 1 : -1, {
      skip: (r2, l11, a2) => {
        if (r2.isWidget()) if (this.openWidget) this.builder.continueWidget(a2 - l11);
        else {
          let h3 = a2 > 0 || l11 < r2.length ? yt4.of(r2.widget, this.view, a2 - l11, r2.flags & 496, this.cache.maybeReuse(r2)) : this.cache.reuse(r2);
          h3.flags & 256 ? (h3.flags &= -2, this.builder.addBlockWidget(h3)) : (this.builder.ensureLine(null), this.builder.addInlineWidget(h3, n22, o4), o4 = n22.length);
        }
        else if (r2.isText()) this.builder.ensureLine(null), !l11 && a2 == r2.length ? this.builder.addText(r2.text, n22, o4, this.cache.reuse(r2)) : (this.cache.add(r2), this.builder.addText(r2.text.slice(l11, a2), n22, o4)), o4 = n22.length;
        else if (r2.isLine()) r2.flags &= -2, this.cache.reused.set(r2, 1), this.builder.addLine(r2);
        else if (r2 instanceof Et4) this.cache.add(r2);
        else if (r2 instanceof V10) this.builder.ensureLine(null), this.builder.addMark(r2, n22, o4), this.cache.reused.set(r2, 1), o4 = n22.length;
        else return false;
        this.openWidget = false;
      },
      enter: (r2) => {
        r2.isLine() ? this.builder.addLineStart(r2.attrs, this.cache.maybeReuse(r2)) : (this.cache.add(r2), r2 instanceof V10 && n22.unshift(r2.mark)), this.openWidget = false;
      },
      leave: (r2) => {
        r2.isLine() ? n22.length && (n22.length = o4 = 0) : r2 instanceof V10 && (n22.shift(), o4 = Math.min(o4, n22.length));
      },
      break: () => {
        this.builder.addBreak(), this.openWidget = false;
      }
    }), this.text.skip(t5);
  }
  emit(t5, e4) {
    let i9 = null, n22 = this.builder, o4 = 0, r2 = T7.spans(this.decorations, t5, e4, {
      point: (l11, a2, h3, c4, f2, d5) => {
        if (h3 instanceof mt4) {
          if (this.disallowBlockEffectsFor[d5]) {
            if (h3.block) throw new RangeError("Block decorations may not be specified via plugins");
            if (a2 > this.view.state.doc.lineAt(l11).to) throw new RangeError("Decorations that replace line breaks may not be specified via plugins");
          }
          if (o4 = c4.length, f2 > c4.length) n22.continueWidget(a2 - l11);
          else {
            let u5 = h3.widget || (h3.block ? ft5.block : ft5.inline), p5 = Oo(h3), g6 = this.cache.findWidget(u5, a2 - l11, p5) || yt4.of(u5, this.view, a2 - l11, p5);
            h3.block ? (h3.startSide > 0 && n22.addLineStartIfNotCovered(i9), n22.addBlockWidget(g6)) : (n22.ensureLine(i9), n22.addInlineWidget(g6, c4, f2));
          }
          i9 = null;
        } else i9 = Lo(i9, h3);
        a2 > l11 && this.text.skip(a2 - l11);
      },
      span: (l11, a2, h3, c4) => {
        for (let f2 = l11; f2 < a2; ) {
          let d5 = this.text.next(Math.min(512, a2 - f2));
          d5 == null ? (n22.addLineStartIfNotCovered(i9), n22.addBreak(), f2++) : (n22.ensureLine(i9), n22.addText(d5, h3, c4), f2 += d5.length), i9 = null;
        }
      }
    });
    n22.addLineStartIfNotCovered(i9), this.openWidget = r2 > o4, this.openMarks = r2;
  }
  forward(t5, e4, i9 = 1) {
    e4 - t5 <= 10 ? this.old.advance(e4 - t5, i9, this.reuseWalker) : (this.old.advance(5, -1, this.reuseWalker), this.old.advance(e4 - t5 - 10, -1), this.old.advance(5, i9, this.reuseWalker));
  }
  getCompositionContext(t5) {
    let e4 = [], i9 = null;
    for (let n22 = t5.parentNode; ; n22 = n22.parentNode) {
      let o4 = B9.get(n22);
      if (n22 == this.view.contentDOM) break;
      o4 instanceof V10 ? e4.push(o4) : o4?.isLine() ? i9 = o4 : n22.nodeName == "DIV" && !i9 && n22 != this.view.contentDOM ? i9 = new Bt5(n22, Mn2) : e4.push(V10.of(new Ut4({
        tagName: n22.nodeName.toLowerCase(),
        attributes: co2(n22)
      }), n22));
    }
    return {
      line: i9,
      marks: e4
    };
  }
};
function ms2(s99, t5) {
  let e4 = (i9) => {
    for (let n22 of i9.children) if ((t5 ? n22.isText() : n22.length) || e4(n22)) return true;
    return false;
  };
  return e4(s99);
}
function Oo(s99) {
  let t5 = s99.isReplace ? (s99.startSide < 0 ? 64 : 0) | (s99.endSide > 0 ? 128 : 0) : s99.startSide > 0 ? 32 : 16;
  return s99.block && (t5 |= 256), t5;
}
var Mn2 = {
  class: "cm-line"
};
function Lo(s99, t5) {
  let e4 = t5.spec.attributes, i9 = t5.spec.class;
  return !e4 && !i9 || (s99 || (s99 = {
    class: "cm-line"
  }), e4 && Zi2(e4, s99), i9 && (s99.class += " " + i9)), s99;
}
function Ro(s99) {
  let t5 = [];
  for (let e4 = s99.parents.length; e4 > 1; e4--) {
    let i9 = e4 == s99.parents.length ? s99.tile : s99.parents[e4].tile;
    i9 instanceof V10 && t5.push(i9.mark);
  }
  return t5;
}
function Xe6(s99) {
  let t5 = B9.get(s99);
  return t5 && t5.setDOM(s99.cloneNode()), s99;
}
var ft5 = class extends et4 {
  constructor(t5) {
    super(), this.tag = t5;
  }
  eq(t5) {
    return t5.tag == this.tag;
  }
  toDOM() {
    return document.createElement(this.tag);
  }
  updateDOM(t5) {
    return t5.nodeName.toLowerCase() == this.tag;
  }
  get isHidden() {
    return true;
  }
};
ft5.inline = new ft5("span");
ft5.block = new ft5("div");
var $e4 = new class extends et4 {
  toDOM() {
    return document.createElement("br");
  }
  get isHidden() {
    return true;
  }
  get editable() {
    return true;
  }
}();
var Oe6 = class {
  constructor(t5) {
    this.view = t5, this.decorations = [], this.blockWrappers = [], this.dynamicDecorationMap = [
      false
    ], this.domChanged = null, this.hasComposition = null, this.editContextFormatting = T8.none, this.lastCompositionAfterCursor = false, this.minWidth = 0, this.minWidthFrom = 0, this.minWidthTo = 0, this.impreciseAnchor = null, this.impreciseHead = null, this.forceSelection = false, this.lastUpdate = Date.now(), this.updateDeco(), this.tile = new Rt4(t5, t5.contentDOM), this.updateInner([
      new q8(0, 0, 0, t5.state.doc.length)
    ], null);
  }
  update(t5) {
    var e4;
    let i9 = t5.changedRanges;
    this.minWidth > 0 && i9.length && (i9.every(({ fromA: c4, toA: f2 }) => f2 < this.minWidthFrom || c4 > this.minWidthTo) ? (this.minWidthFrom = t5.changes.mapPos(this.minWidthFrom, 1), this.minWidthTo = t5.changes.mapPos(this.minWidthTo, 1)) : this.minWidth = this.minWidthFrom = this.minWidthTo = 0), this.updateEditContextFormatting(t5);
    let n22 = -1;
    this.view.inputState.composing >= 0 && !this.view.observer.editContext && (!((e4 = this.domChanged) === null || e4 === void 0) && e4.newSel ? n22 = this.domChanged.newSel.head : !Fo(t5.changes, this.hasComposition) && !t5.selectionSet && (n22 = t5.state.selection.main.head));
    let o4 = n22 > -1 ? Eo(this.view, t5.changes, n22) : null;
    if (this.domChanged = null, this.hasComposition) {
      let { from: c4, to: f2 } = this.hasComposition;
      i9 = new q8(c4, f2, t5.changes.mapPos(c4, -1), t5.changes.mapPos(f2, 1)).addToSet(i9.slice());
    }
    this.hasComposition = o4 ? {
      from: o4.range.fromB,
      to: o4.range.toB
    } : null, (y8.ie || y8.chrome) && !o4 && t5 && t5.state.doc.lines != t5.startState.doc.lines && (this.forceSelection = true);
    let r2 = this.decorations, l11 = this.blockWrappers;
    this.updateDeco();
    let a2 = No(r2, this.decorations, t5.changes);
    a2.length && (i9 = q8.extendWithRanges(i9, a2));
    let h3 = Wo(l11, this.blockWrappers, t5.changes);
    return h3.length && (i9 = q8.extendWithRanges(i9, h3)), o4 && !i9.some((c4) => c4.fromA <= o4.range.fromA && c4.toA >= o4.range.toA) && (i9 = o4.range.addToSet(i9.slice())), this.tile.flags & 2 && i9.length == 0 ? false : (this.updateInner(i9, o4), t5.transactions.length && (this.lastUpdate = Date.now()), true);
  }
  updateInner(t5, e4) {
    this.view.viewState.mustMeasureContent = true;
    let { observer: i9 } = this.view;
    i9.ignore(() => {
      if (e4 || t5.length) {
        let r2 = this.tile, l11 = new gi2(this.view, r2, this.blockWrappers, this.decorations, this.dynamicDecorationMap);
        this.tile = l11.run(t5, e4), mi2(r2, l11.cache.reused);
      }
      this.tile.dom.style.height = this.view.viewState.contentHeight / this.view.scaleY + "px", this.tile.dom.style.flexBasis = this.minWidth ? this.minWidth + "px" : "";
      let o4 = y8.chrome || y8.ios ? {
        node: i9.selectionRange.focusNode,
        written: false
      } : void 0;
      this.tile.sync(o4), o4 && (o4.written || i9.selectionRange.focusNode != o4.node || !this.tile.dom.contains(o4.node)) && (this.forceSelection = true), this.tile.dom.style.height = "";
    });
    let n22 = [];
    if (this.view.viewport.from || this.view.viewport.to < this.view.state.doc.length) for (let o4 of this.tile.children) o4.isWidget() && o4.widget instanceof jt5 && n22.push(o4.dom);
    i9.updateGaps(n22);
  }
  updateEditContextFormatting(t5) {
    this.editContextFormatting = this.editContextFormatting.map(t5.changes);
    for (let e4 of t5.transactions) for (let i9 of e4.effects) i9.is(wn2) && (this.editContextFormatting = i9.value);
  }
  updateSelection(t5 = false, e4 = false) {
    (t5 || !this.view.observer.selectionRange.focusNode) && this.view.observer.readSelectionRange();
    let { dom: i9 } = this.tile, n22 = this.view.root.activeElement, o4 = n22 == i9, r2 = !o4 && !(this.view.state.facet(tt6) || i9.tabIndex > -1) && be7(i9, this.view.observer.selectionRange) && !(n22 && i9.contains(n22));
    if (!(o4 || e4 || r2)) return;
    let l11 = this.forceSelection;
    this.forceSelection = false;
    let a2 = this.view.state.selection.main, h3, c4;
    if (a2.empty ? c4 = h3 = this.inlineDOMNearPos(a2.anchor, a2.assoc || 1) : (c4 = this.inlineDOMNearPos(a2.head, a2.head == a2.from ? 1 : -1), h3 = this.inlineDOMNearPos(a2.anchor, a2.anchor == a2.from ? 1 : -1)), y8.gecko && a2.empty && !this.hasComposition && Bo(h3)) {
      let d5 = document.createTextNode("");
      this.view.observer.ignore(() => h3.node.insertBefore(d5, h3.node.childNodes[h3.offset] || null)), h3 = c4 = new G7(d5, 0), l11 = true;
    }
    let f2 = this.view.observer.selectionRange;
    (l11 || !f2.focusNode || (!qt3(h3.node, h3.offset, f2.anchorNode, f2.anchorOffset) || !qt3(c4.node, c4.offset, f2.focusNode, f2.focusOffset)) && !this.suppressWidgetCursorChange(f2, a2)) && (this.view.observer.ignore(() => {
      y8.android && y8.chrome && i9.contains(f2.focusNode) && Vo(f2.focusNode, i9) && (i9.blur(), i9.focus({
        preventScroll: true
      }));
      let d5 = Jt3(this.view.root);
      if (d5) if (a2.empty) {
        if (y8.gecko) {
          let u5 = Ho(h3.node, h3.offset);
          if (u5 && u5 != 3) {
            let p5 = (u5 == 1 ? tn3 : en3)(h3.node, h3.offset);
            p5 && (h3 = new G7(p5.node, p5.offset));
          }
        }
        d5.collapse(h3.node, h3.offset), a2.bidiLevel != null && d5.caretBidiLevel !== void 0 && (d5.caretBidiLevel = a2.bidiLevel);
      } else if (d5.extend) {
        d5.collapse(h3.node, h3.offset);
        try {
          d5.extend(c4.node, c4.offset);
        } catch {
        }
      } else {
        let u5 = document.createRange();
        a2.anchor > a2.head && ([h3, c4] = [
          c4,
          h3
        ]), u5.setEnd(c4.node, c4.offset), u5.setStart(h3.node, h3.offset), d5.removeAllRanges(), d5.addRange(u5);
      }
      r2 && this.view.root.activeElement == i9 && (i9.blur(), n22 && n22.focus());
    }), this.view.observer.setSelectionRange(h3, c4)), this.impreciseAnchor = h3.precise ? null : new G7(f2.anchorNode, f2.anchorOffset), this.impreciseHead = c4.precise ? null : new G7(f2.focusNode, f2.focusOffset);
  }
  suppressWidgetCursorChange(t5, e4) {
    return this.hasComposition && e4.empty && qt3(t5.focusNode, t5.focusOffset, t5.anchorNode, t5.anchorOffset) && this.posFromDOM(t5.focusNode, t5.focusOffset) == e4.head;
  }
  enforceCursorAssoc() {
    if (this.hasComposition) return;
    let { view: t5 } = this, e4 = t5.state.selection.main, i9 = Jt3(t5.root), { anchorNode: n22, anchorOffset: o4 } = t5.observer.selectionRange;
    if (!i9 || !e4.empty || !e4.assoc || !i9.modify) return;
    let r2 = this.lineAt(e4.head, e4.assoc);
    if (!r2) return;
    let l11 = r2.posAtStart;
    if (e4.head == l11 || e4.head == l11 + r2.length) return;
    let a2 = this.coordsAt(e4.head, -1), h3 = this.coordsAt(e4.head, 1);
    if (!a2 || !h3 || a2.bottom > h3.top) return;
    let c4 = this.domAtPos(e4.head + e4.assoc, e4.assoc);
    i9.collapse(c4.node, c4.offset), i9.modify("move", e4.assoc < 0 ? "forward" : "backward", "lineboundary"), t5.observer.readSelectionRange();
    let f2 = t5.observer.selectionRange;
    t5.docView.posFromDOM(f2.anchorNode, f2.anchorOffset) != e4.from && i9.collapse(n22, o4);
  }
  posFromDOM(t5, e4) {
    let i9 = this.tile.nearest(t5);
    if (!i9) return this.tile.dom.compareDocumentPosition(t5) & 2 ? 0 : this.view.state.doc.length;
    let n22 = i9.posAtStart;
    if (i9.isComposite()) {
      let o4;
      if (t5 == i9.dom) o4 = i9.dom.childNodes[e4];
      else {
        let r2 = it6(t5) == 0 ? 0 : e4 == 0 ? -1 : 1;
        for (; ; ) {
          let l11 = t5.parentNode;
          if (l11 == i9.dom) break;
          r2 == 0 && l11.firstChild != l11.lastChild && (t5 == l11.firstChild ? r2 = -1 : r2 = 1), t5 = l11;
        }
        r2 < 0 ? o4 = t5 : o4 = t5.nextSibling;
      }
      if (o4 == i9.dom.firstChild) return n22;
      for (; o4 && !B9.get(o4); ) o4 = o4.nextSibling;
      if (!o4) return n22 + i9.length;
      for (let r2 = 0, l11 = n22; ; r2++) {
        let a2 = i9.children[r2];
        if (a2.dom == o4) return l11;
        l11 += a2.length + a2.breakAfter;
      }
    } else return i9.isText() ? t5 == i9.dom ? n22 + e4 : n22 + (e4 ? i9.length : 0) : n22;
  }
  domAtPos(t5, e4) {
    let { tile: i9, offset: n22 } = this.tile.resolveBlock(t5, e4);
    return i9.isWidget() ? i9.domPosFor(t5, e4) : i9.domIn(n22, e4);
  }
  inlineDOMNearPos(t5, e4) {
    let i9, n22 = -1, o4 = false, r2, l11 = -1, a2 = false;
    return this.tile.blockTiles((h3, c4) => {
      if (h3.isWidget()) {
        if (h3.flags & 32 && c4 >= t5) return true;
        h3.flags & 16 && (o4 = true);
      } else {
        let f2 = c4 + h3.length;
        if (c4 <= t5 && (i9 = h3, n22 = t5 - c4, o4 = f2 < t5), f2 >= t5 && !r2 && (r2 = h3, l11 = t5 - c4, a2 = c4 > t5), c4 > t5 && r2) return true;
      }
    }), !i9 && !r2 ? this.domAtPos(t5, e4) : (o4 && r2 ? i9 = null : a2 && i9 && (r2 = null), i9 && e4 < 0 || !r2 ? i9.domIn(n22, e4) : r2.domIn(l11, e4));
  }
  coordsAt(t5, e4) {
    let { tile: i9, offset: n22 } = this.tile.resolveBlock(t5, e4);
    return i9.isWidget() ? i9.widget instanceof jt5 ? null : i9.coordsInWidget(n22, e4, true) : i9.coordsIn(n22, e4);
  }
  lineAt(t5, e4) {
    let { tile: i9 } = this.tile.resolveBlock(t5, e4);
    return i9.isLine() ? i9 : null;
  }
  coordsForChar(t5) {
    let { tile: e4, offset: i9 } = this.tile.resolveBlock(t5, 1);
    if (!e4.isLine()) return null;
    function n22(o4, r2) {
      if (o4.isComposite()) for (let l11 of o4.children) {
        if (l11.length >= r2) {
          let a2 = n22(l11, r2);
          if (a2) return a2;
        }
        if (r2 -= l11.length, r2 < 0) break;
      }
      else if (o4.isText() && r2 < o4.length) {
        let l11 = ee6(o4.text, r2);
        if (l11 == r2) return null;
        let a2 = te8(o4.dom, r2, l11).getClientRects();
        for (let h3 = 0; h3 < a2.length; h3++) {
          let c4 = a2[h3];
          if (h3 == a2.length - 1 || c4.top < c4.bottom && c4.left < c4.right) return c4;
        }
      }
      return null;
    }
    return n22(e4, i9);
  }
  measureVisibleLineHeights(t5) {
    let e4 = [], { from: i9, to: n22 } = t5, o4 = this.view.contentDOM.clientWidth, r2 = o4 > Math.max(this.view.scrollDOM.clientWidth, this.minWidth) + 1, l11 = -1, a2 = this.view.textDirection == R9.LTR, h3 = 0, c4 = (f2, d5, u5) => {
      for (let p5 = 0; p5 < f2.children.length && !(d5 > n22); p5++) {
        let g6 = f2.children[p5], m9 = d5 + g6.length, b9 = g6.dom.getBoundingClientRect(), { height: w11 } = b9;
        if (u5 && !p5 && (h3 += b9.top - u5.top), g6 instanceof at6) m9 > i9 && c4(g6, d5, b9);
        else if (d5 >= i9 && (h3 > 0 && e4.push(-h3), e4.push(w11 + h3), h3 = 0, r2)) {
          let M14 = g6.dom.lastChild, A11 = M14 ? zt3(M14) : [];
          if (A11.length) {
            let v8 = A11[A11.length - 1], x11 = a2 ? v8.right - b9.left : b9.right - v8.left;
            x11 > l11 && (l11 = x11, this.minWidth = o4, this.minWidthFrom = d5, this.minWidthTo = m9);
          }
        }
        u5 && p5 == f2.children.length - 1 && (h3 += u5.bottom - b9.bottom), d5 = m9 + g6.breakAfter;
      }
    };
    return c4(this.tile, 0, null), e4;
  }
  textDirectionAt(t5) {
    let { tile: e4 } = this.tile.resolveBlock(t5, 1);
    return getComputedStyle(e4.dom).direction == "rtl" ? R9.RTL : R9.LTR;
  }
  measureTextSize() {
    let t5 = this.tile.blockTiles((r2) => {
      if (r2.isLine() && r2.children.length && r2.length <= 20) {
        let l11 = 0, a2;
        for (let h3 of r2.children) {
          if (!h3.isText() || /[^ -~]/.test(h3.text)) return;
          let c4 = zt3(h3.dom);
          if (c4.length != 1) return;
          l11 += c4[0].width, a2 = c4[0].height;
        }
        if (l11) return {
          lineHeight: r2.dom.getBoundingClientRect().height,
          charWidth: l11 / r2.length,
          textHeight: a2
        };
      }
    });
    if (t5) return t5;
    let e4 = document.createElement("div"), i9, n22, o4;
    return e4.className = "cm-line", e4.style.width = "99999px", e4.style.position = "absolute", e4.textContent = "abc def ghi jkl mno pqr stu", this.view.observer.ignore(() => {
      this.tile.dom.appendChild(e4);
      let r2 = zt3(e4.firstChild)[0];
      i9 = e4.getBoundingClientRect().height, n22 = r2 && r2.width ? r2.width / 27 : 7, o4 = r2 && r2.height ? r2.height : i9, e4.remove();
    }), {
      lineHeight: i9,
      charWidth: n22,
      textHeight: o4
    };
  }
  computeBlockGapDeco() {
    let t5 = [], e4 = this.view.viewState;
    for (let i9 = 0, n22 = 0; ; n22++) {
      let o4 = n22 == e4.viewports.length ? null : e4.viewports[n22], r2 = o4 ? o4.from - 1 : this.view.state.doc.length;
      if (r2 > i9) {
        let l11 = (e4.lineBlockAt(r2).bottom - e4.lineBlockAt(i9).top) / this.view.scaleY;
        t5.push(T8.replace({
          widget: new jt5(l11),
          block: true,
          inclusive: true,
          isBlockGap: true
        }).range(i9, r2));
      }
      if (!o4) break;
      i9 = o4.to + 1;
    }
    return T8.set(t5);
  }
  updateDeco() {
    let t5 = 1, e4 = this.view.state.facet(Ke5).map((o4) => (this.dynamicDecorationMap[t5++] = typeof o4 == "function") ? o4(this.view) : o4), i9 = false, n22 = this.view.state.facet(ns2).map((o4, r2) => {
      let l11 = typeof o4 == "function";
      return l11 && (i9 = true), l11 ? o4(this.view) : o4;
    });
    for (n22.length && (this.dynamicDecorationMap[t5++] = i9, e4.push(T7.join(n22))), this.decorations = [
      this.editContextFormatting,
      ...e4,
      this.computeBlockGapDeco(),
      this.view.viewState.lineGapDeco
    ]; t5 < this.decorations.length; ) this.dynamicDecorationMap[t5++] = false;
    this.blockWrappers = this.view.state.facet(vn2).map((o4) => typeof o4 == "function" ? o4(this.view) : o4);
  }
  scrollIntoView(t5) {
    if (t5.isSnapshot) {
      let h3 = this.view.viewState.lineBlockAt(t5.range.head);
      this.view.scrollDOM.scrollTop = h3.top - t5.yMargin, this.view.scrollDOM.scrollLeft = t5.xMargin;
      return;
    }
    for (let h3 of this.view.state.facet(yn2)) try {
      if (h3(this.view, t5.range, t5)) return true;
    } catch (c4) {
      U9(this.view.state, c4, "scroll handler");
    }
    let { range: e4 } = t5, i9 = this.coordsAt(e4.head, e4.empty ? e4.assoc : e4.head > e4.anchor ? -1 : 1), n22;
    if (!i9) return;
    !e4.empty && (n22 = this.coordsAt(e4.anchor, e4.anchor > e4.head ? -1 : 1)) && (i9 = {
      left: Math.min(i9.left, n22.left),
      top: Math.min(i9.top, n22.top),
      right: Math.max(i9.right, n22.right),
      bottom: Math.max(i9.bottom, n22.bottom)
    });
    let o4 = os2(this.view), r2 = {
      left: i9.left - o4.left,
      top: i9.top - o4.top,
      right: i9.right + o4.right,
      bottom: i9.bottom + o4.bottom
    }, { offsetWidth: l11, offsetHeight: a2 } = this.view.scrollDOM;
    po2(this.view.scrollDOM, r2, e4.head < e4.anchor ? -1 : 1, t5.x, t5.y, Math.max(Math.min(t5.xMargin, l11), -l11), Math.max(Math.min(t5.yMargin, a2), -a2), this.view.textDirection == R9.LTR);
  }
  lineHasWidget(t5) {
    let e4 = (i9) => i9.isWidget() || i9.children.some(e4);
    return e4(this.tile.resolveBlock(t5, 1).tile);
  }
  destroy() {
    mi2(this.tile);
  }
};
function mi2(s99, t5) {
  let e4 = t5?.get(s99);
  if (e4 != 1) {
    e4 == null && s99.destroy();
    for (let i9 of s99.children) mi2(i9, t5);
  }
}
function Bo(s99) {
  return s99.node.nodeType == 1 && s99.node.firstChild && (s99.offset == 0 || s99.node.childNodes[s99.offset - 1].contentEditable == "false") && (s99.offset == s99.node.childNodes.length || s99.node.childNodes[s99.offset].contentEditable == "false");
}
function kn2(s99, t5) {
  let e4 = s99.observer.selectionRange;
  if (!e4.focusNode) return null;
  let i9 = tn3(e4.focusNode, e4.focusOffset), n22 = en3(e4.focusNode, e4.focusOffset), o4 = i9 || n22;
  if (n22 && i9 && n22.node != i9.node) {
    let l11 = B9.get(n22.node);
    if (!l11 || l11.isText() && l11.text != n22.node.nodeValue) o4 = n22;
    else if (s99.docView.lastCompositionAfterCursor) {
      let a2 = B9.get(i9.node);
      !a2 || a2.isText() && a2.text != i9.node.nodeValue || (o4 = n22);
    }
  }
  if (s99.docView.lastCompositionAfterCursor = o4 != i9, !o4) return null;
  let r2 = t5 - o4.offset;
  return {
    from: r2,
    to: r2 + o4.node.nodeValue.length,
    node: o4.node
  };
}
function Eo(s99, t5, e4) {
  let i9 = kn2(s99, e4);
  if (!i9) return null;
  let { node: n22, from: o4, to: r2 } = i9, l11 = n22.nodeValue;
  if (/[\n\r]/.test(l11) || s99.state.doc.sliceString(i9.from, i9.to) != l11) return null;
  let a2 = t5.invertedDesc;
  return {
    range: new q8(a2.mapPos(o4), a2.mapPos(r2), o4, r2),
    text: n22
  };
}
function Ho(s99, t5) {
  return s99.nodeType != 1 ? 0 : (t5 && s99.childNodes[t5 - 1].contentEditable == "false" ? 1 : 0) | (t5 < s99.childNodes.length && s99.childNodes[t5].contentEditable == "false" ? 2 : 0);
}
var Po = class {
  constructor() {
    this.changes = [];
  }
  compareRange(t5, e4) {
    Tt5(t5, e4, this.changes);
  }
  comparePoint(t5, e4) {
    Tt5(t5, e4, this.changes);
  }
  boundChange(t5) {
    Tt5(t5, t5, this.changes);
  }
};
function No(s99, t5, e4) {
  let i9 = new Po();
  return T7.compare(s99, t5, e4, i9), i9.changes;
}
var bi2 = class {
  constructor() {
    this.changes = [];
  }
  compareRange(t5, e4) {
    Tt5(t5, e4, this.changes);
  }
  comparePoint() {
  }
  boundChange(t5) {
    Tt5(t5, t5, this.changes);
  }
};
function Wo(s99, t5, e4) {
  let i9 = new bi2();
  return T7.compare(s99, t5, e4, i9), i9.changes;
}
function Vo(s99, t5) {
  for (let e4 = s99; e4 && e4 != t5; e4 = e4.assignedSlot || e4.parentNode) if (e4.nodeType == 1 && e4.contentEditable == "false") return true;
  return false;
}
function Fo(s99, t5) {
  let e4 = false;
  return t5 && s99.iterChangedRanges((i9, n22) => {
    i9 < t5.to && n22 > t5.from && (e4 = true);
  }), e4;
}
var jt5 = class extends et4 {
  constructor(t5) {
    super(), this.height = t5;
  }
  toDOM() {
    let t5 = document.createElement("div");
    return t5.className = "cm-gap", this.updateDOM(t5), t5;
  }
  eq(t5) {
    return t5.height == this.height;
  }
  updateDOM(t5) {
    return t5.style.height = this.height + "px", true;
  }
  get editable() {
    return true;
  }
  get estimatedHeight() {
    return this.height;
  }
  ignoreEvent() {
    return false;
  }
};
function Io(s99, t5, e4 = 1) {
  let i9 = s99.charCategorizer(t5), n22 = s99.doc.lineAt(t5), o4 = t5 - n22.from;
  if (n22.length == 0) return x8.cursor(t5);
  o4 == 0 ? e4 = 1 : o4 == n22.length && (e4 = -1);
  let r2 = o4, l11 = o4;
  e4 < 0 ? r2 = ee6(n22.text, o4, false) : l11 = ee6(n22.text, o4);
  let a2 = i9(n22.text.slice(r2, l11));
  for (; r2 > 0; ) {
    let h3 = ee6(n22.text, r2, false);
    if (i9(n22.text.slice(h3, r2)) != a2) break;
    r2 = h3;
  }
  for (; l11 < n22.length; ) {
    let h3 = ee6(n22.text, l11);
    if (i9(n22.text.slice(l11, h3)) != a2) break;
    l11 = h3;
  }
  return x8.range(r2 + n22.from, l11 + n22.from);
}
function zo(s99, t5, e4, i9, n22) {
  let o4 = Math.round((i9 - t5.left) * s99.defaultCharacterWidth);
  if (s99.lineWrapping && e4.height > s99.defaultLineHeight * 1.5) {
    let l11 = s99.viewState.heightOracle.textHeight, a2 = Math.floor((n22 - e4.top - (s99.defaultLineHeight - l11) * 0.5) / l11);
    o4 += a2 * s99.viewState.heightOracle.lineLength;
  }
  let r2 = s99.state.sliceDoc(e4.from, e4.to);
  return e4.from + ht5(r2, o4, s99.state.tabSize);
}
function yi2(s99, t5, e4) {
  let i9 = s99.lineBlockAt(t5);
  if (Array.isArray(i9.type)) {
    let n22;
    for (let o4 of i9.type) {
      if (o4.from > t5) break;
      if (!(o4.to < t5)) {
        if (o4.from < t5 && o4.to > t5) return o4;
        (!n22 || o4.type == P8.Text && (n22.type != o4.type || (e4 < 0 ? o4.from < t5 : o4.to > t5))) && (n22 = o4);
      }
    }
    return n22 || i9;
  }
  return i9;
}
function qo(s99, t5, e4, i9) {
  let n22 = yi2(s99, t5.head, t5.assoc || -1), o4 = !i9 || n22.type != P8.Text || !(s99.lineWrapping || n22.widgetLineBreaks) ? null : s99.coordsAtPos(t5.assoc < 0 && t5.head > n22.from ? t5.head - 1 : t5.head);
  if (o4) {
    let r2 = s99.dom.getBoundingClientRect(), l11 = s99.textDirectionAt(n22.from), a2 = s99.posAtCoords({
      x: e4 == (l11 == R9.LTR) ? r2.right - 1 : r2.left + 1,
      y: (o4.top + o4.bottom) / 2
    });
    if (a2 != null) return x8.cursor(a2, e4 ? -1 : 1);
  }
  return x8.cursor(e4 ? n22.to : n22.from, e4 ? -1 : 1);
}
function bs2(s99, t5, e4, i9) {
  let n22 = s99.state.doc.lineAt(t5.head), o4 = s99.bidiSpans(n22), r2 = s99.textDirectionAt(n22.from);
  for (let l11 = t5, a2 = null; ; ) {
    let h3 = hn3(n22, o4, r2, l11, e4), c4 = an3;
    if (!h3) {
      if (n22.number == (e4 ? s99.state.doc.lines : 1)) return l11;
      c4 = `
`, n22 = s99.state.doc.line(n22.number + (e4 ? 1 : -1)), o4 = s99.bidiSpans(n22), h3 = s99.visualLineSide(n22, !e4);
    }
    if (a2) {
      if (!a2(c4)) return l11;
    } else {
      if (!i9) return h3;
      a2 = i9(c4);
    }
    l11 = h3;
  }
}
function Ko(s99, t5, e4) {
  let i9 = s99.state.charCategorizer(t5), n22 = i9(e4);
  return (o4) => {
    let r2 = i9(o4);
    return n22 == M9.Space && (n22 = r2), n22 == r2;
  };
}
function _o(s99, t5, e4, i9) {
  let n22 = t5.head, o4 = e4 ? 1 : -1;
  if (n22 == (e4 ? s99.state.doc.length : 0)) return x8.cursor(n22, t5.assoc);
  let r2 = t5.goalColumn, l11, a2 = s99.contentDOM.getBoundingClientRect(), h3 = s99.coordsAtPos(n22, t5.assoc || -1), c4 = s99.documentTop;
  if (h3) r2 == null && (r2 = h3.left - a2.left), l11 = o4 < 0 ? h3.top : h3.bottom;
  else {
    let u5 = s99.viewState.lineBlockAt(n22);
    r2 == null && (r2 = Math.min(a2.right - a2.left, s99.defaultCharacterWidth * (n22 - u5.from))), l11 = (o4 < 0 ? u5.top : u5.bottom) + c4;
  }
  let f2 = a2.left + r2, d5 = i9 ?? s99.viewState.heightOracle.textHeight >> 1;
  for (let u5 = 0; ; u5 += 10) {
    let p5 = l11 + (d5 + u5) * o4, g6 = wi2(s99, {
      x: f2,
      y: p5
    }, false, o4);
    return x8.cursor(g6.pos, g6.assoc, void 0, r2);
  }
}
function Yt3(s99, t5, e4) {
  for (; ; ) {
    let i9 = 0;
    for (let n22 of s99) n22.between(t5 - 1, t5 + 1, (o4, r2, l11) => {
      if (t5 > o4 && t5 < r2) {
        let a2 = i9 || e4 || (t5 - o4 < r2 - t5 ? -1 : 1);
        t5 = a2 < 0 ? o4 : r2, i9 = a2;
      }
    });
    if (!i9) return t5;
  }
}
function An2(s99, t5) {
  let e4 = null;
  for (let i9 = 0; i9 < t5.ranges.length; i9++) {
    let n22 = t5.ranges[i9], o4 = null;
    if (n22.empty) {
      let r2 = Yt3(s99, n22.from, 0);
      r2 != n22.from && (o4 = x8.cursor(r2, -1));
    } else {
      let r2 = Yt3(s99, n22.from, -1), l11 = Yt3(s99, n22.to, 1);
      (r2 != n22.from || l11 != n22.to) && (o4 = x8.range(n22.from == n22.anchor ? r2 : l11, n22.from == n22.head ? r2 : l11));
    }
    o4 && (e4 || (e4 = t5.ranges.slice()), e4[i9] = o4);
  }
  return e4 ? x8.create(e4, t5.mainIndex) : t5;
}
function Ge5(s99, t5, e4) {
  let i9 = Yt3(s99.state.facet(ne8).map((n22) => n22(s99)), e4.from, t5.head > e4.from ? -1 : 1);
  return i9 == e4.from ? e4 : x8.cursor(i9, i9 < e4.from ? 1 : -1);
}
var z9 = class {
  constructor(t5, e4) {
    this.pos = t5, this.assoc = e4;
  }
};
function wi2(s99, t5, e4, i9) {
  let n22 = s99.contentDOM.getBoundingClientRect(), o4 = n22.top + s99.viewState.paddingTop, { x: r2, y: l11 } = t5, a2 = l11 - o4, h3;
  for (; ; ) {
    if (a2 < 0) return new z9(0, 1);
    if (a2 > s99.viewState.docHeight) return new z9(s99.state.doc.length, -1);
    if (h3 = s99.elementAtHeight(a2), i9 == null) break;
    if (h3.type == P8.Text) {
      let d5 = s99.docView.coordsAt(i9 < 0 ? h3.from : h3.to, i9);
      if (d5 && (i9 < 0 ? d5.top <= a2 + o4 : d5.bottom >= a2 + o4)) break;
    }
    let f2 = s99.viewState.heightOracle.textHeight / 2;
    a2 = i9 > 0 ? h3.bottom + f2 : h3.top - f2;
  }
  if (s99.viewport.from >= h3.to || s99.viewport.to <= h3.from) {
    if (e4) return null;
    if (h3.type == P8.Text) {
      let f2 = zo(s99, n22, h3, r2, l11);
      return new z9(f2, f2 == h3.from ? 1 : -1);
    }
  }
  if (h3.type != P8.Text) return a2 < (h3.top + h3.bottom) / 2 ? new z9(h3.from, 1) : new z9(h3.to, -1);
  let c4 = s99.docView.lineAt(h3.from, 2);
  return (!c4 || c4.length != h3.length) && (c4 = s99.docView.lineAt(h3.from, -2)), Tn3(s99, c4, h3.from, r2, l11);
}
function Tn3(s99, t5, e4, i9, n22) {
  let o4 = -1, r2 = null, l11 = 1e9, a2 = 1e9, h3 = n22, c4 = n22, f2 = (d5, u5) => {
    for (let p5 = 0; p5 < d5.length; p5++) {
      let g6 = d5[p5];
      if (g6.top == g6.bottom) continue;
      let m9 = g6.left > i9 ? g6.left - i9 : g6.right < i9 ? i9 - g6.right : 0, b9 = g6.top > n22 ? g6.top - n22 : g6.bottom < n22 ? n22 - g6.bottom : 0;
      g6.top <= c4 && g6.bottom >= h3 && (h3 = Math.min(g6.top, h3), c4 = Math.max(g6.bottom, c4), b9 = 0), (o4 < 0 || (b9 - a2 || m9 - l11) < 0) && (o4 >= 0 && a2 && l11 < m9 && r2.top <= c4 - 2 && r2.bottom >= h3 + 2 ? a2 = 0 : (o4 = u5, l11 = m9, a2 = b9, r2 = g6));
    }
  };
  if (t5.isText()) {
    for (let u5 = 0; u5 < t5.length; ) {
      let p5 = ee6(t5.text, u5);
      if (f2(te8(t5.dom, u5, p5).getClientRects(), u5), !l11 && !a2) break;
      u5 = p5;
    }
    return i9 > (r2.left + r2.right) / 2 == (ys2(s99, o4 + e4) == R9.LTR) ? new z9(e4 + ee6(t5.text, o4), -1) : new z9(e4 + o4, 1);
  } else {
    if (!t5.length) return new z9(e4, 1);
    for (let g6 = 0; g6 < t5.children.length; g6++) {
      let m9 = t5.children[g6];
      if (m9.flags & 48) continue;
      let b9 = (m9.dom.nodeType == 1 ? m9.dom : te8(m9.dom, 0, m9.length)).getClientRects();
      if (f2(b9, g6), !l11 && !a2) break;
    }
    let d5 = t5.children[o4], u5 = t5.posBefore(d5, e4);
    return d5.isComposite() || d5.isText() ? Tn3(s99, d5, u5, Math.max(r2.left, Math.min(r2.right, i9)), n22) : i9 > (r2.left + r2.right) / 2 == (ys2(s99, o4 + e4) == R9.LTR) ? new z9(u5 + d5.length, -1) : new z9(u5, 1);
  }
}
function ys2(s99, t5) {
  let e4 = s99.state.doc.lineAt(t5);
  return s99.bidiSpans(e4)[j8.find(s99.bidiSpans(e4), t5 - e4.from, -1, 1)].dir;
}
var Wt3 = "\uFFFF";
var xi2 = class {
  constructor(t5, e4) {
    this.points = t5, this.view = e4, this.text = "", this.lineSeparator = e4.state.facet(P7.lineSeparator);
  }
  append(t5) {
    this.text += t5;
  }
  lineBreak() {
    this.text += Wt3;
  }
  readRange(t5, e4) {
    if (!t5) return this;
    let i9 = t5.parentNode;
    for (let n22 = t5; ; ) {
      this.findPointBefore(i9, n22);
      let o4 = this.text.length;
      this.readNode(n22);
      let r2 = B9.get(n22), l11 = n22.nextSibling;
      if (l11 == e4) {
        r2?.breakAfter && !l11 && i9 != this.view.contentDOM && this.lineBreak();
        break;
      }
      let a2 = B9.get(l11);
      (r2 && a2 ? r2.breakAfter : (r2 ? r2.breakAfter : Ae6(n22)) || Ae6(l11) && (n22.nodeName != "BR" || r2?.isWidget()) && this.text.length > o4) && !Yo(l11, e4) && this.lineBreak(), n22 = l11;
    }
    return this.findPointBefore(i9, e4), this;
  }
  readTextNode(t5) {
    let e4 = t5.nodeValue;
    for (let i9 of this.points) i9.node == t5 && (i9.pos = this.text.length + Math.min(i9.offset, e4.length));
    for (let i9 = 0, n22 = this.lineSeparator ? null : /\r\n?|\n/g; ; ) {
      let o4 = -1, r2 = 1, l11;
      if (this.lineSeparator ? (o4 = e4.indexOf(this.lineSeparator, i9), r2 = this.lineSeparator.length) : (l11 = n22.exec(e4)) && (o4 = l11.index, r2 = l11[0].length), this.append(e4.slice(i9, o4 < 0 ? e4.length : o4)), o4 < 0) break;
      if (this.lineBreak(), r2 > 1) for (let a2 of this.points) a2.node == t5 && a2.pos > this.text.length && (a2.pos -= r2 - 1);
      i9 = o4 + r2;
    }
  }
  readNode(t5) {
    let e4 = B9.get(t5), i9 = e4 && e4.overrideDOMText;
    if (i9 != null) {
      this.findPointInside(t5, i9.length);
      for (let n22 = i9.iter(); !n22.next().done; ) n22.lineBreak ? this.lineBreak() : this.append(n22.value);
    } else t5.nodeType == 3 ? this.readTextNode(t5) : t5.nodeName == "BR" ? t5.nextSibling && this.lineBreak() : t5.nodeType == 1 && this.readRange(t5.firstChild, null);
  }
  findPointBefore(t5, e4) {
    for (let i9 of this.points) i9.node == t5 && t5.childNodes[i9.offset] == e4 && (i9.pos = this.text.length);
  }
  findPointInside(t5, e4) {
    for (let i9 of this.points) (t5.nodeType == 3 ? i9.node == t5 : t5.contains(i9.node)) && (i9.pos = this.text.length + (jo(t5, i9.node, i9.offset) ? e4 : 0));
  }
};
function jo(s99, t5, e4) {
  for (; ; ) {
    if (!t5 || e4 < it6(t5)) return false;
    if (t5 == s99) return true;
    e4 = ct4(t5) + 1, t5 = t5.parentNode;
  }
}
function Yo(s99, t5) {
  let e4;
  for (; !(s99 == t5 || !s99); s99 = s99.nextSibling) {
    let i9 = B9.get(s99);
    if (!i9?.isWidget()) return false;
    i9 && (e4 || (e4 = [])).push(i9);
  }
  if (e4) for (let i9 of e4) {
    let n22 = i9.overrideDOMText;
    if (n22?.length) return false;
  }
  return true;
}
var Le8 = class {
  constructor(t5, e4) {
    this.node = t5, this.offset = e4, this.pos = -1;
  }
};
var vi = class {
  constructor(t5, e4, i9, n22) {
    this.typeOver = n22, this.bounds = null, this.text = "", this.domChanged = e4 > -1;
    let { impreciseHead: o4, impreciseAnchor: r2 } = t5.docView;
    if (t5.state.readOnly && e4 > -1) this.newSel = null;
    else if (e4 > -1 && (this.bounds = Dn2(t5.docView.tile, e4, i9, 0))) {
      let l11 = o4 || r2 ? [] : $o(t5), a2 = new xi2(l11, t5);
      a2.readRange(this.bounds.startDOM, this.bounds.endDOM), this.text = a2.text, this.newSel = Go(l11, this.bounds.from);
    } else {
      let l11 = t5.observer.selectionRange, a2 = o4 && o4.node == l11.focusNode && o4.offset == l11.focusOffset || !ni2(t5.contentDOM, l11.focusNode) ? t5.state.selection.main.head : t5.docView.posFromDOM(l11.focusNode, l11.focusOffset), h3 = r2 && r2.node == l11.anchorNode && r2.offset == l11.anchorOffset || !ni2(t5.contentDOM, l11.anchorNode) ? t5.state.selection.main.anchor : t5.docView.posFromDOM(l11.anchorNode, l11.anchorOffset), c4 = t5.viewport;
      if ((y8.ios || y8.chrome) && t5.state.selection.main.empty && a2 != h3 && (c4.from > 0 || c4.to < t5.state.doc.length)) {
        let f2 = Math.min(a2, h3), d5 = Math.max(a2, h3), u5 = c4.from - f2, p5 = c4.to - d5;
        (u5 == 0 || u5 == 1 || f2 == 0) && (p5 == 0 || p5 == -1 || d5 == t5.state.doc.length) && (a2 = 0, h3 = t5.state.doc.length);
      }
      t5.inputState.composing > -1 && t5.state.selection.ranges.length > 1 ? this.newSel = t5.state.selection.replaceRange(x8.range(h3, a2)) : this.newSel = x8.single(h3, a2);
    }
  }
};
function Dn2(s99, t5, e4, i9) {
  if (s99.isComposite()) {
    let n22 = -1, o4 = -1, r2 = -1, l11 = -1;
    for (let a2 = 0, h3 = i9, c4 = i9; a2 < s99.children.length; a2++) {
      let f2 = s99.children[a2], d5 = h3 + f2.length;
      if (h3 < t5 && d5 > e4) return Dn2(f2, t5, e4, h3);
      if (d5 >= t5 && n22 == -1 && (n22 = a2, o4 = h3), h3 > e4 && f2.dom.parentNode == s99.dom) {
        r2 = a2, l11 = c4;
        break;
      }
      c4 = d5, h3 = d5 + f2.breakAfter;
    }
    return {
      from: o4,
      to: l11 < 0 ? i9 + s99.length : l11,
      startDOM: (n22 ? s99.children[n22 - 1].dom.nextSibling : null) || s99.dom.firstChild,
      endDOM: r2 < s99.children.length && r2 >= 0 ? s99.children[r2].dom : null
    };
  } else return s99.isText() ? {
    from: i9,
    to: i9 + s99.length,
    startDOM: s99.dom,
    endDOM: s99.dom.nextSibling
  } : null;
}
function On2(s99, t5) {
  let e4, { newSel: i9 } = t5, n22 = s99.state.selection.main, o4 = s99.inputState.lastKeyTime > Date.now() - 100 ? s99.inputState.lastKeyCode : -1;
  if (t5.bounds) {
    let { from: r2, to: l11 } = t5.bounds, a2 = n22.from, h3 = null;
    (o4 === 8 || y8.android && t5.text.length < l11 - r2) && (a2 = n22.to, h3 = "end");
    let c4 = Ln2(s99.state.doc.sliceString(r2, l11, Wt3), t5.text, a2 - r2, h3);
    c4 && (y8.chrome && o4 == 13 && c4.toB == c4.from + 2 && t5.text.slice(c4.from, c4.toB) == Wt3 + Wt3 && c4.toB--, e4 = {
      from: r2 + c4.from,
      to: r2 + c4.toA,
      insert: m7.of(t5.text.slice(c4.from, c4.toB).split(Wt3))
    });
  } else i9 && (!s99.hasFocus && s99.state.facet(tt6) || i9.main.eq(n22)) && (i9 = null);
  if (!e4 && !i9) return false;
  if (!e4 && t5.typeOver && !n22.empty && i9 && i9.main.empty ? e4 = {
    from: n22.from,
    to: n22.to,
    insert: s99.state.doc.slice(n22.from, n22.to)
  } : (y8.mac || y8.android) && e4 && e4.from == e4.to && e4.from == n22.head - 1 && /^\. ?$/.test(e4.insert.toString()) && s99.contentDOM.getAttribute("autocorrect") == "off" ? (i9 && e4.insert.length == 2 && (i9 = x8.single(i9.main.anchor - 1, i9.main.head - 1)), e4 = {
    from: e4.from,
    to: e4.to,
    insert: m7.of([
      e4.insert.toString().replace(".", " ")
    ])
  }) : e4 && e4.from >= n22.from && e4.to <= n22.to && (e4.from != n22.from || e4.to != n22.to) && n22.to - n22.from - (e4.to - e4.from) <= 4 ? e4 = {
    from: n22.from,
    to: n22.to,
    insert: s99.state.doc.slice(n22.from, e4.from).append(e4.insert).append(s99.state.doc.slice(e4.to, n22.to))
  } : s99.state.doc.lineAt(n22.from).to < n22.to && s99.docView.lineHasWidget(n22.to) && s99.inputState.insertingTextAt > Date.now() - 50 ? e4 = {
    from: n22.from,
    to: n22.to,
    insert: s99.state.toText(s99.inputState.insertingText)
  } : y8.chrome && e4 && e4.from == e4.to && e4.from == n22.head && e4.insert.toString() == `
 ` && s99.lineWrapping && (i9 && (i9 = x8.single(i9.main.anchor - 1, i9.main.head - 1)), e4 = {
    from: n22.from,
    to: n22.to,
    insert: m7.of([
      " "
    ])
  }), e4) return rs2(s99, e4, i9, o4);
  if (i9 && !i9.main.eq(n22)) {
    let r2 = false, l11 = "select";
    return s99.inputState.lastSelectionTime > Date.now() - 50 && (s99.inputState.lastSelectionOrigin == "select" && (r2 = true), l11 = s99.inputState.lastSelectionOrigin, l11 == "select.pointer" && (i9 = An2(s99.state.facet(ne8).map((a2) => a2(s99)), i9))), s99.dispatch({
      selection: i9,
      scrollIntoView: r2,
      userEvent: l11
    }), true;
  } else return false;
}
function rs2(s99, t5, e4, i9 = -1) {
  if (y8.ios && s99.inputState.flushIOSKey(t5)) return true;
  let n22 = s99.state.selection.main;
  if (y8.android && (t5.to == n22.to && (t5.from == n22.from || t5.from == n22.from - 1 && s99.state.sliceDoc(t5.from, n22.from) == " ") && t5.insert.length == 1 && t5.insert.lines == 2 && Dt5(s99.contentDOM, "Enter", 13) || (t5.from == n22.from - 1 && t5.to == n22.to && t5.insert.length == 0 || i9 == 8 && t5.insert.length < t5.to - t5.from && t5.to > n22.head) && Dt5(s99.contentDOM, "Backspace", 8) || t5.from == n22.from && t5.to == n22.to + 1 && t5.insert.length == 0 && Dt5(s99.contentDOM, "Delete", 46))) return true;
  let o4 = t5.insert.toString();
  s99.inputState.composing >= 0 && s99.inputState.composing++;
  let r2, l11 = () => r2 || (r2 = Xo(s99, t5, e4));
  return s99.state.facet(pn).some((a2) => a2(s99, t5.from, t5.to, o4, l11)) || s99.dispatch(l11()), true;
}
function Xo(s99, t5, e4) {
  let i9, n22 = s99.state, o4 = n22.selection.main, r2 = -1;
  if (t5.from == t5.to && t5.from < o4.from || t5.from > o4.to) {
    let a2 = t5.from < o4.from ? -1 : 1, h3 = a2 < 0 ? o4.from : o4.to, c4 = Yt3(n22.facet(ne8).map((f2) => f2(s99)), h3, a2);
    t5.from == c4 && (r2 = c4);
  }
  if (r2 > -1) i9 = {
    changes: t5,
    selection: x8.cursor(t5.from + t5.insert.length, -1)
  };
  else if (t5.from >= o4.from && t5.to <= o4.to && t5.to - t5.from >= (o4.to - o4.from) / 3 && (!e4 || e4.main.empty && e4.main.from == t5.from + t5.insert.length) && s99.inputState.composing < 0) {
    let a2 = o4.from < t5.from ? n22.sliceDoc(o4.from, t5.from) : "", h3 = o4.to > t5.to ? n22.sliceDoc(t5.to, o4.to) : "";
    i9 = n22.replaceSelection(s99.state.toText(a2 + t5.insert.sliceString(0, void 0, s99.state.lineBreak) + h3));
  } else {
    let a2 = n22.changes(t5), h3 = e4 && e4.main.to <= a2.newLength ? e4.main : void 0;
    if (n22.selection.ranges.length > 1 && (s99.inputState.composing >= 0 || s99.inputState.compositionPendingChange) && t5.to <= o4.to + 10 && t5.to >= o4.to - 10) {
      let c4 = s99.state.sliceDoc(t5.from, t5.to), f2, d5 = e4 && kn2(s99, e4.main.head);
      if (d5) {
        let p5 = t5.insert.length - (t5.to - t5.from);
        f2 = {
          from: d5.from,
          to: d5.to - p5
        };
      } else f2 = s99.state.doc.lineAt(o4.head);
      let u5 = o4.to - t5.to;
      i9 = n22.changeByRange((p5) => {
        if (p5.from == o4.from && p5.to == o4.to) return {
          changes: a2,
          range: h3 || p5.map(a2)
        };
        let g6 = p5.to - u5, m9 = g6 - c4.length;
        if (s99.state.sliceDoc(m9, g6) != c4 || g6 >= f2.from && m9 <= f2.to) return {
          range: p5
        };
        let b9 = n22.changes({
          from: m9,
          to: g6,
          insert: t5.insert
        }), w11 = p5.to - o4.to;
        return {
          changes: b9,
          range: h3 ? x8.range(Math.max(0, h3.anchor + w11), Math.max(0, h3.head + w11)) : p5.map(b9)
        };
      });
    } else i9 = {
      changes: a2,
      selection: h3 && n22.selection.replaceRange(h3)
    };
  }
  let l11 = "input.type";
  return (s99.composing || s99.inputState.compositionPendingChange && s99.inputState.compositionEndedAt > Date.now() - 50) && (s99.inputState.compositionPendingChange = false, l11 += ".compose", s99.inputState.compositionFirstChange && (l11 += ".start", s99.inputState.compositionFirstChange = false)), n22.update(i9, {
    userEvent: l11,
    scrollIntoView: true
  });
}
function Ln2(s99, t5, e4, i9) {
  let n22 = Math.min(s99.length, t5.length), o4 = 0;
  for (; o4 < n22 && s99.charCodeAt(o4) == t5.charCodeAt(o4); ) o4++;
  if (o4 == n22 && s99.length == t5.length) return null;
  let r2 = s99.length, l11 = t5.length;
  for (; r2 > 0 && l11 > 0 && s99.charCodeAt(r2 - 1) == t5.charCodeAt(l11 - 1); ) r2--, l11--;
  if (i9 == "end") {
    let a2 = Math.max(0, o4 - Math.min(r2, l11));
    e4 -= r2 + a2 - o4;
  }
  if (r2 < o4 && s99.length < t5.length) {
    let a2 = e4 <= o4 && e4 >= r2 ? o4 - e4 : 0;
    o4 -= a2, l11 = o4 + (l11 - r2), r2 = o4;
  } else if (l11 < o4) {
    let a2 = e4 <= o4 && e4 >= l11 ? o4 - e4 : 0;
    o4 -= a2, r2 = o4 + (r2 - l11), l11 = o4;
  }
  return {
    from: o4,
    toA: r2,
    toB: l11
  };
}
function $o(s99) {
  let t5 = [];
  if (s99.root.activeElement != s99.contentDOM) return t5;
  let { anchorNode: e4, anchorOffset: i9, focusNode: n22, focusOffset: o4 } = s99.observer.selectionRange;
  return e4 && (t5.push(new Le8(e4, i9)), (n22 != e4 || o4 != i9) && t5.push(new Le8(n22, o4))), t5;
}
function Go(s99, t5) {
  if (s99.length == 0) return null;
  let e4 = s99[0].pos, i9 = s99.length == 2 ? s99[1].pos : e4;
  return e4 > -1 && i9 > -1 ? x8.single(e4 + t5, i9 + t5) : null;
}
var Si2 = class {
  setSelectionOrigin(t5) {
    this.lastSelectionOrigin = t5, this.lastSelectionTime = Date.now();
  }
  constructor(t5) {
    this.view = t5, this.lastKeyCode = 0, this.lastKeyTime = 0, this.lastTouchTime = 0, this.lastFocusTime = 0, this.lastScrollTop = 0, this.lastScrollLeft = 0, this.pendingIOSKey = void 0, this.tabFocusMode = -1, this.lastSelectionOrigin = null, this.lastSelectionTime = 0, this.lastContextMenu = 0, this.scrollHandlers = [], this.handlers = /* @__PURE__ */ Object.create(null), this.composing = -1, this.compositionFirstChange = null, this.compositionEndedAt = 0, this.compositionPendingKey = false, this.compositionPendingChange = false, this.insertingText = "", this.insertingTextAt = 0, this.mouseSelection = null, this.draggedContent = null, this.handleEvent = this.handleEvent.bind(this), this.notifiedFocused = t5.hasFocus, y8.safari && t5.contentDOM.addEventListener("input", () => null), y8.gecko && hr2(t5.contentDOM.ownerDocument);
  }
  handleEvent(t5) {
    !ir2(this.view, t5) || this.ignoreDuringComposition(t5) || t5.type == "keydown" && this.keydown(t5) || (this.view.updateState != 0 ? Promise.resolve().then(() => this.runHandlers(t5.type, t5)) : this.runHandlers(t5.type, t5));
  }
  runHandlers(t5, e4) {
    let i9 = this.handlers[t5];
    if (i9) {
      for (let n22 of i9.observers) n22(this.view, e4);
      for (let n22 of i9.handlers) {
        if (e4.defaultPrevented) break;
        if (n22(this.view, e4)) {
          e4.preventDefault();
          break;
        }
      }
    }
  }
  ensureHandlers(t5) {
    let e4 = Uo(t5), i9 = this.handlers, n22 = this.view.contentDOM;
    for (let o4 in e4) if (o4 != "scroll") {
      let r2 = !e4[o4].handlers.length, l11 = i9[o4];
      l11 && r2 != !l11.handlers.length && (n22.removeEventListener(o4, this.handleEvent), l11 = null), l11 || n22.addEventListener(o4, this.handleEvent, {
        passive: r2
      });
    }
    for (let o4 in i9) o4 != "scroll" && !e4[o4] && n22.removeEventListener(o4, this.handleEvent);
    this.handlers = e4;
  }
  keydown(t5) {
    if (this.lastKeyCode = t5.keyCode, this.lastKeyTime = Date.now(), t5.keyCode == 9 && this.tabFocusMode > -1 && (!this.tabFocusMode || Date.now() <= this.tabFocusMode)) return true;
    if (this.tabFocusMode > 0 && t5.keyCode != 27 && Bn2.indexOf(t5.keyCode) < 0 && (this.tabFocusMode = -1), y8.android && y8.chrome && !t5.synthetic && (t5.keyCode == 13 || t5.keyCode == 8)) return this.view.observer.delayAndroidKey(t5.key, t5.keyCode), true;
    let e4;
    return y8.ios && !t5.synthetic && !t5.altKey && !t5.metaKey && ((e4 = Rn2.find((i9) => i9.keyCode == t5.keyCode)) && !t5.ctrlKey || Qo.indexOf(t5.key) > -1 && t5.ctrlKey && !t5.shiftKey) ? (this.pendingIOSKey = e4 || t5, setTimeout(() => this.flushIOSKey(), 250), true) : (t5.keyCode != 229 && this.view.observer.forceFlush(), false);
  }
  flushIOSKey(t5) {
    let e4 = this.pendingIOSKey;
    return !e4 || e4.key == "Enter" && t5 && t5.from < t5.to && /^\S+$/.test(t5.insert.toString()) ? false : (this.pendingIOSKey = void 0, Dt5(this.view.contentDOM, e4.key, e4.keyCode, e4 instanceof KeyboardEvent ? e4 : void 0));
  }
  ignoreDuringComposition(t5) {
    return !/^key/.test(t5.type) || t5.synthetic ? false : this.composing > 0 ? true : y8.safari && !y8.ios && this.compositionPendingKey && Date.now() - this.compositionEndedAt < 100 ? (this.compositionPendingKey = false, true) : false;
  }
  startMouseSelection(t5) {
    this.mouseSelection && this.mouseSelection.destroy(), this.mouseSelection = t5;
  }
  update(t5) {
    this.view.observer.update(t5), this.mouseSelection && this.mouseSelection.update(t5), this.draggedContent && t5.docChanged && (this.draggedContent = this.draggedContent.map(t5.changes)), t5.transactions.length && (this.lastKeyCode = this.lastSelectionTime = 0);
  }
  destroy() {
    this.mouseSelection && this.mouseSelection.destroy();
  }
};
function ws2(s99, t5) {
  return (e4, i9) => {
    try {
      return t5.call(s99, i9, e4);
    } catch (n22) {
      U9(e4.state, n22);
    }
  };
}
function Uo(s99) {
  let t5 = /* @__PURE__ */ Object.create(null);
  function e4(i9) {
    return t5[i9] || (t5[i9] = {
      observers: [],
      handlers: []
    });
  }
  for (let i9 of s99) {
    let n22 = i9.spec, o4 = n22 && n22.plugin.domEventHandlers, r2 = n22 && n22.plugin.domEventObservers;
    if (o4) for (let l11 in o4) {
      let a2 = o4[l11];
      a2 && e4(l11).handlers.push(ws2(i9.value, a2));
    }
    if (r2) for (let l11 in r2) {
      let a2 = r2[l11];
      a2 && e4(l11).observers.push(ws2(i9.value, a2));
    }
  }
  for (let i9 in X9) e4(i9).handlers.push(X9[i9]);
  for (let i9 in K9) e4(i9).observers.push(K9[i9]);
  return t5;
}
var Rn2 = [
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
    key: "Enter",
    keyCode: 13,
    inputType: "insertLineBreak"
  },
  {
    key: "Delete",
    keyCode: 46,
    inputType: "deleteContentForward"
  }
];
var Qo = "dthko";
var Bn2 = [
  16,
  17,
  18,
  20,
  91,
  92,
  224,
  225
];
var he7 = 6;
function ce10(s99) {
  return Math.max(0, s99) * 0.7 + 8;
}
function Jo(s99, t5) {
  return Math.max(Math.abs(s99.clientX - t5.clientX), Math.abs(s99.clientY - t5.clientY));
}
var Ci2 = class {
  constructor(t5, e4, i9, n22) {
    this.view = t5, this.startEvent = e4, this.style = i9, this.mustSelect = n22, this.scrollSpeed = {
      x: 0,
      y: 0
    }, this.scrolling = -1, this.lastEvent = e4, this.scrollParents = go2(t5.contentDOM), this.atoms = t5.state.facet(ne8).map((r2) => r2(t5));
    let o4 = t5.contentDOM.ownerDocument;
    o4.addEventListener("mousemove", this.move = this.move.bind(this)), o4.addEventListener("mouseup", this.up = this.up.bind(this)), this.extend = e4.shiftKey, this.multiple = t5.state.facet(P7.allowMultipleSelections) && Zo(t5, e4), this.dragging = er2(t5, e4) && Pn2(e4) == 1 ? null : false;
  }
  start(t5) {
    this.dragging === false && this.select(t5);
  }
  move(t5) {
    if (t5.buttons == 0) return this.destroy();
    if (this.dragging || this.dragging == null && Jo(this.startEvent, t5) < 10) return;
    this.select(this.lastEvent = t5);
    let e4 = 0, i9 = 0, n22 = 0, o4 = 0, r2 = this.view.win.innerWidth, l11 = this.view.win.innerHeight;
    this.scrollParents.x && ({ left: n22, right: r2 } = this.scrollParents.x.getBoundingClientRect()), this.scrollParents.y && ({ top: o4, bottom: l11 } = this.scrollParents.y.getBoundingClientRect());
    let a2 = os2(this.view);
    t5.clientX - a2.left <= n22 + he7 ? e4 = -ce10(n22 - t5.clientX) : t5.clientX + a2.right >= r2 - he7 && (e4 = ce10(t5.clientX - r2)), t5.clientY - a2.top <= o4 + he7 ? i9 = -ce10(o4 - t5.clientY) : t5.clientY + a2.bottom >= l11 - he7 && (i9 = ce10(t5.clientY - l11)), this.setScrollSpeed(e4, i9);
  }
  up(t5) {
    this.dragging == null && this.select(this.lastEvent), this.dragging || t5.preventDefault(), this.destroy();
  }
  destroy() {
    this.setScrollSpeed(0, 0);
    let t5 = this.view.contentDOM.ownerDocument;
    t5.removeEventListener("mousemove", this.move), t5.removeEventListener("mouseup", this.up), this.view.inputState.mouseSelection = this.view.inputState.draggedContent = null;
  }
  setScrollSpeed(t5, e4) {
    this.scrollSpeed = {
      x: t5,
      y: e4
    }, t5 || e4 ? this.scrolling < 0 && (this.scrolling = setInterval(() => this.scroll(), 50)) : this.scrolling > -1 && (clearInterval(this.scrolling), this.scrolling = -1);
  }
  scroll() {
    let { x: t5, y: e4 } = this.scrollSpeed;
    t5 && this.scrollParents.x && (this.scrollParents.x.scrollLeft += t5, t5 = 0), e4 && this.scrollParents.y && (this.scrollParents.y.scrollTop += e4, e4 = 0), (t5 || e4) && this.view.win.scrollBy(t5, e4), this.dragging === false && this.select(this.lastEvent);
  }
  select(t5) {
    let { view: e4 } = this, i9 = An2(this.atoms, this.style.get(t5, this.extend, this.multiple));
    (this.mustSelect || !i9.eq(e4.state.selection, this.dragging === false)) && this.view.dispatch({
      selection: i9,
      userEvent: "select.pointer"
    }), this.mustSelect = false;
  }
  update(t5) {
    t5.transactions.some((e4) => e4.isUserEvent("input.type")) ? this.destroy() : this.style.update(t5) && setTimeout(() => this.select(this.lastEvent), 20);
  }
};
function Zo(s99, t5) {
  let e4 = s99.state.facet(cn2);
  return e4.length ? e4[0](t5) : y8.mac ? t5.metaKey : t5.ctrlKey;
}
function tr2(s99, t5) {
  let e4 = s99.state.facet(fn);
  return e4.length ? e4[0](t5) : y8.mac ? !t5.altKey : !t5.ctrlKey;
}
function er2(s99, t5) {
  let { main: e4 } = s99.state.selection;
  if (e4.empty) return false;
  let i9 = Jt3(s99.root);
  if (!i9 || i9.rangeCount == 0) return true;
  let n22 = i9.getRangeAt(0).getClientRects();
  for (let o4 = 0; o4 < n22.length; o4++) {
    let r2 = n22[o4];
    if (r2.left <= t5.clientX && r2.right >= t5.clientX && r2.top <= t5.clientY && r2.bottom >= t5.clientY) return true;
  }
  return false;
}
function ir2(s99, t5) {
  if (!t5.bubbles) return true;
  if (t5.defaultPrevented) return false;
  for (let e4 = t5.target, i9; e4 != s99.contentDOM; e4 = e4.parentNode) if (!e4 || e4.nodeType == 11 || (i9 = B9.get(e4)) && i9.isWidget() && !i9.isHidden && i9.widget.ignoreEvent(t5)) return false;
  return true;
}
var X9 = /* @__PURE__ */ Object.create(null);
var K9 = /* @__PURE__ */ Object.create(null);
var En2 = y8.ie && y8.ie_version < 15 || y8.ios && y8.webkit_version < 604;
function sr2(s99) {
  let t5 = s99.dom.parentNode;
  if (!t5) return;
  let e4 = t5.appendChild(document.createElement("textarea"));
  e4.style.cssText = "position: fixed; left: -10000px; top: 10px", e4.focus(), setTimeout(() => {
    s99.focus(), e4.remove(), Hn2(s99, e4.value);
  }, 50);
}
function _e7(s99, t5, e4) {
  for (let i9 of s99.facet(t5)) e4 = i9(e4, s99);
  return e4;
}
function Hn2(s99, t5) {
  t5 = _e7(s99.state, is2, t5);
  let { state: e4 } = s99, i9, n22 = 1, o4 = e4.toText(t5), r2 = o4.lines == e4.selection.ranges.length;
  if (Mi2 != null && e4.selection.ranges.every((a2) => a2.empty) && Mi2 == o4.toString()) {
    let a2 = -1;
    i9 = e4.changeByRange((h3) => {
      let c4 = e4.doc.lineAt(h3.from);
      if (c4.from == a2) return {
        range: h3
      };
      a2 = c4.from;
      let f2 = e4.toText((r2 ? o4.line(n22++).text : t5) + e4.lineBreak);
      return {
        changes: {
          from: c4.from,
          insert: f2
        },
        range: x8.cursor(h3.from + f2.length)
      };
    });
  } else r2 ? i9 = e4.changeByRange((a2) => {
    let h3 = o4.line(n22++);
    return {
      changes: {
        from: a2.from,
        to: a2.to,
        insert: h3.text
      },
      range: x8.cursor(a2.from + h3.length)
    };
  }) : i9 = e4.replaceSelection(o4);
  s99.dispatch(i9, {
    userEvent: "input.paste",
    scrollIntoView: true
  });
}
K9.scroll = (s99) => {
  s99.inputState.lastScrollTop = s99.scrollDOM.scrollTop, s99.inputState.lastScrollLeft = s99.scrollDOM.scrollLeft;
};
X9.keydown = (s99, t5) => (s99.inputState.setSelectionOrigin("select"), t5.keyCode == 27 && s99.inputState.tabFocusMode != 0 && (s99.inputState.tabFocusMode = Date.now() + 2e3), false);
K9.touchstart = (s99, t5) => {
  s99.inputState.lastTouchTime = Date.now(), s99.inputState.setSelectionOrigin("select.pointer");
};
K9.touchmove = (s99) => {
  s99.inputState.setSelectionOrigin("select.pointer");
};
X9.mousedown = (s99, t5) => {
  if (s99.observer.flush(), s99.inputState.lastTouchTime > Date.now() - 2e3) return false;
  let e4 = null;
  for (let i9 of s99.state.facet(dn2)) if (e4 = i9(s99, t5), e4) break;
  if (!e4 && t5.button == 0 && (e4 = or2(s99, t5)), e4) {
    let i9 = !s99.hasFocus;
    s99.inputState.startMouseSelection(new Ci2(s99, t5, e4, i9)), i9 && s99.observer.ignore(() => {
      Js2(s99.contentDOM);
      let o4 = s99.root.activeElement;
      o4 && !o4.contains(s99.contentDOM) && o4.blur();
    });
    let n22 = s99.inputState.mouseSelection;
    if (n22) return n22.start(t5), n22.dragging === false;
  } else s99.inputState.setSelectionOrigin("select.pointer");
  return false;
};
function xs2(s99, t5, e4, i9) {
  if (i9 == 1) return x8.cursor(t5, e4);
  if (i9 == 2) return Io(s99.state, t5, e4);
  {
    let n22 = s99.docView.lineAt(t5, e4), o4 = s99.state.doc.lineAt(n22 ? n22.posAtEnd : t5), r2 = n22 ? n22.posAtStart : o4.from, l11 = n22 ? n22.posAtEnd : o4.to;
    return l11 < s99.state.doc.length && l11 == o4.to && l11++, x8.range(r2, l11);
  }
}
var nr2 = y8.ie && y8.ie_version <= 11;
var vs2 = null;
var Ss2 = 0;
var Cs2 = 0;
function Pn2(s99) {
  if (!nr2) return s99.detail;
  let t5 = vs2, e4 = Cs2;
  return vs2 = s99, Cs2 = Date.now(), Ss2 = !t5 || e4 > Date.now() - 400 && Math.abs(t5.clientX - s99.clientX) < 2 && Math.abs(t5.clientY - s99.clientY) < 2 ? (Ss2 + 1) % 3 : 1;
}
function or2(s99, t5) {
  let e4 = s99.posAndSideAtCoords({
    x: t5.clientX,
    y: t5.clientY
  }, false), i9 = Pn2(t5), n22 = s99.state.selection;
  return {
    update(o4) {
      o4.docChanged && (e4.pos = o4.changes.mapPos(e4.pos), n22 = n22.map(o4.changes));
    },
    get(o4, r2, l11) {
      let a2 = s99.posAndSideAtCoords({
        x: o4.clientX,
        y: o4.clientY
      }, false), h3, c4 = xs2(s99, a2.pos, a2.assoc, i9);
      if (e4.pos != a2.pos && !r2) {
        let f2 = xs2(s99, e4.pos, e4.assoc, i9), d5 = Math.min(f2.from, c4.from), u5 = Math.max(f2.to, c4.to);
        c4 = d5 < c4.from ? x8.range(d5, u5) : x8.range(u5, d5);
      }
      return r2 ? n22.replaceRange(n22.main.extend(c4.from, c4.to)) : l11 && i9 == 1 && n22.ranges.length > 1 && (h3 = rr2(n22, a2.pos)) ? h3 : l11 ? n22.addRange(c4) : x8.create([
        c4
      ]);
    }
  };
}
function rr2(s99, t5) {
  for (let e4 = 0; e4 < s99.ranges.length; e4++) {
    let { from: i9, to: n22 } = s99.ranges[e4];
    if (i9 <= t5 && n22 >= t5) return x8.create(s99.ranges.slice(0, e4).concat(s99.ranges.slice(e4 + 1)), s99.mainIndex == e4 ? 0 : s99.mainIndex - (s99.mainIndex > e4 ? 1 : 0));
  }
  return null;
}
X9.dragstart = (s99, t5) => {
  let { selection: { main: e4 } } = s99.state;
  if (t5.target.draggable) {
    let n22 = s99.docView.tile.nearest(t5.target);
    if (n22 && n22.isWidget()) {
      let o4 = n22.posAtStart, r2 = o4 + n22.length;
      (o4 >= e4.to || r2 <= e4.from) && (e4 = x8.range(o4, r2));
    }
  }
  let { inputState: i9 } = s99;
  return i9.mouseSelection && (i9.mouseSelection.dragging = true), i9.draggedContent = e4, t5.dataTransfer && (t5.dataTransfer.setData("Text", _e7(s99.state, ss2, s99.state.sliceDoc(e4.from, e4.to))), t5.dataTransfer.effectAllowed = "copyMove"), false;
};
X9.dragend = (s99) => (s99.inputState.draggedContent = null, false);
function Ms2(s99, t5, e4, i9) {
  if (e4 = _e7(s99.state, is2, e4), !e4) return;
  let n22 = s99.posAtCoords({
    x: t5.clientX,
    y: t5.clientY
  }, false), { draggedContent: o4 } = s99.inputState, r2 = i9 && o4 && tr2(s99, t5) ? {
    from: o4.from,
    to: o4.to
  } : null, l11 = {
    from: n22,
    insert: e4
  }, a2 = s99.state.changes(r2 ? [
    r2,
    l11
  ] : l11);
  s99.focus(), s99.dispatch({
    changes: a2,
    selection: {
      anchor: a2.mapPos(n22, -1),
      head: a2.mapPos(n22, 1)
    },
    userEvent: r2 ? "move.drop" : "input.drop"
  }), s99.inputState.draggedContent = null;
}
X9.drop = (s99, t5) => {
  if (!t5.dataTransfer) return false;
  if (s99.state.readOnly) return true;
  let e4 = t5.dataTransfer.files;
  if (e4 && e4.length) {
    let i9 = Array(e4.length), n22 = 0, o4 = () => {
      ++n22 == e4.length && Ms2(s99, t5, i9.filter((r2) => r2 != null).join(s99.state.lineBreak), false);
    };
    for (let r2 = 0; r2 < e4.length; r2++) {
      let l11 = new FileReader();
      l11.onerror = o4, l11.onload = () => {
        /[\x00-\x08\x0e-\x1f]{2}/.test(l11.result) || (i9[r2] = l11.result), o4();
      }, l11.readAsText(e4[r2]);
    }
    return true;
  } else {
    let i9 = t5.dataTransfer.getData("Text");
    if (i9) return Ms2(s99, t5, i9, true), true;
  }
  return false;
};
X9.paste = (s99, t5) => {
  if (s99.state.readOnly) return true;
  s99.observer.flush();
  let e4 = En2 ? null : t5.clipboardData;
  return e4 ? (Hn2(s99, e4.getData("text/plain") || e4.getData("text/uri-list")), true) : (sr2(s99), false);
};
function lr2(s99, t5) {
  let e4 = s99.dom.parentNode;
  if (!e4) return;
  let i9 = e4.appendChild(document.createElement("textarea"));
  i9.style.cssText = "position: fixed; left: -10000px; top: 10px", i9.value = t5, i9.focus(), i9.selectionEnd = t5.length, i9.selectionStart = 0, setTimeout(() => {
    i9.remove(), s99.focus();
  }, 50);
}
function ar2(s99) {
  let t5 = [], e4 = [], i9 = false;
  for (let n22 of s99.selection.ranges) n22.empty || (t5.push(s99.sliceDoc(n22.from, n22.to)), e4.push(n22));
  if (!t5.length) {
    let n22 = -1;
    for (let { from: o4 } of s99.selection.ranges) {
      let r2 = s99.doc.lineAt(o4);
      r2.number > n22 && (t5.push(r2.text), e4.push({
        from: r2.from,
        to: Math.min(s99.doc.length, r2.to + 1)
      })), n22 = r2.number;
    }
    i9 = true;
  }
  return {
    text: _e7(s99, ss2, t5.join(s99.lineBreak)),
    ranges: e4,
    linewise: i9
  };
}
var Mi2 = null;
X9.copy = X9.cut = (s99, t5) => {
  let { text: e4, ranges: i9, linewise: n22 } = ar2(s99.state);
  if (!e4 && !n22) return false;
  Mi2 = n22 ? e4 : null, t5.type == "cut" && !s99.state.readOnly && s99.dispatch({
    changes: i9,
    scrollIntoView: true,
    userEvent: "delete.cut"
  });
  let o4 = En2 ? null : t5.clipboardData;
  return o4 ? (o4.clearData(), o4.setData("text/plain", e4), true) : (lr2(s99, e4), false);
};
var Nn2 = L7.define();
function Wn2(s99, t5) {
  let e4 = [];
  for (let i9 of s99.facet(gn2)) {
    let n22 = i9(s99, t5);
    n22 && e4.push(n22);
  }
  return e4.length ? s99.update({
    effects: e4,
    annotations: Nn2.of(true)
  }) : null;
}
function Vn2(s99) {
  setTimeout(() => {
    let t5 = s99.hasFocus;
    if (t5 != s99.inputState.notifiedFocused) {
      let e4 = Wn2(s99.state, t5);
      e4 ? s99.dispatch(e4) : s99.update([]);
    }
  }, 10);
}
K9.focus = (s99) => {
  s99.inputState.lastFocusTime = Date.now(), !s99.scrollDOM.scrollTop && (s99.inputState.lastScrollTop || s99.inputState.lastScrollLeft) && (s99.scrollDOM.scrollTop = s99.inputState.lastScrollTop, s99.scrollDOM.scrollLeft = s99.inputState.lastScrollLeft), Vn2(s99);
};
K9.blur = (s99) => {
  s99.observer.clearSelectionRange(), Vn2(s99);
};
K9.compositionstart = K9.compositionupdate = (s99) => {
  s99.observer.editContext || (s99.inputState.compositionFirstChange == null && (s99.inputState.compositionFirstChange = true), s99.inputState.composing < 0 && (s99.inputState.composing = 0));
};
K9.compositionend = (s99) => {
  s99.observer.editContext || (s99.inputState.composing = -1, s99.inputState.compositionEndedAt = Date.now(), s99.inputState.compositionPendingKey = true, s99.inputState.compositionPendingChange = s99.observer.pendingRecords().length > 0, s99.inputState.compositionFirstChange = null, y8.chrome && y8.android ? s99.observer.flushSoon() : s99.inputState.compositionPendingChange ? Promise.resolve().then(() => s99.observer.flush()) : setTimeout(() => {
    s99.inputState.composing < 0 && s99.docView.hasComposition && s99.update([]);
  }, 50));
};
K9.contextmenu = (s99) => {
  s99.inputState.lastContextMenu = Date.now();
};
X9.beforeinput = (s99, t5) => {
  var e4, i9;
  if ((t5.inputType == "insertText" || t5.inputType == "insertCompositionText") && (s99.inputState.insertingText = t5.data, s99.inputState.insertingTextAt = Date.now()), t5.inputType == "insertReplacementText" && s99.observer.editContext) {
    let o4 = (e4 = t5.dataTransfer) === null || e4 === void 0 ? void 0 : e4.getData("text/plain"), r2 = t5.getTargetRanges();
    if (o4 && r2.length) {
      let l11 = r2[0], a2 = s99.posAtDOM(l11.startContainer, l11.startOffset), h3 = s99.posAtDOM(l11.endContainer, l11.endOffset);
      return rs2(s99, {
        from: a2,
        to: h3,
        insert: s99.state.toText(o4)
      }, null), true;
    }
  }
  let n22;
  if (y8.chrome && y8.android && (n22 = Rn2.find((o4) => o4.inputType == t5.inputType)) && (s99.observer.delayAndroidKey(n22.key, n22.keyCode), n22.key == "Backspace" || n22.key == "Delete")) {
    let o4 = ((i9 = globalThis.visualViewport) === null || i9 === void 0 ? void 0 : i9.height) || 0;
    setTimeout(() => {
      var r2;
      (((r2 = globalThis.visualViewport) === null || r2 === void 0 ? void 0 : r2.height) || 0) > o4 + 10 && s99.hasFocus && (s99.contentDOM.blur(), s99.focus());
    }, 100);
  }
  return y8.ios && t5.inputType == "deleteContentForward" && s99.observer.flushSoon(), y8.safari && t5.inputType == "insertText" && s99.inputState.composing >= 0 && setTimeout(() => K9.compositionend(s99, t5), 20), false;
};
var ks2 = /* @__PURE__ */ new Set();
function hr2(s99) {
  ks2.has(s99) || (ks2.add(s99), s99.addEventListener("copy", () => {
  }), s99.addEventListener("cut", () => {
  }));
}
var As2 = [
  "pre-wrap",
  "normal",
  "pre-line",
  "break-spaces"
];
var wt4 = false;
function ki2() {
  wt4 = false;
}
var Re7 = class {
  constructor(t5) {
    this.lineWrapping = t5, this.doc = m7.empty, this.heightSamples = {}, this.lineHeight = 14, this.charWidth = 7, this.textHeight = 14, this.lineLength = 30;
  }
  heightForGap(t5, e4) {
    let i9 = this.doc.lineAt(e4).number - this.doc.lineAt(t5).number + 1;
    return this.lineWrapping && (i9 += Math.max(0, Math.ceil((e4 - t5 - i9 * this.lineLength * 0.5) / this.lineLength))), this.lineHeight * i9;
  }
  heightForLine(t5) {
    return this.lineWrapping ? (1 + Math.max(0, Math.ceil((t5 - this.lineLength) / Math.max(1, this.lineLength - 5)))) * this.lineHeight : this.lineHeight;
  }
  setDoc(t5) {
    return this.doc = t5, this;
  }
  mustRefreshForWrapping(t5) {
    return As2.indexOf(t5) > -1 != this.lineWrapping;
  }
  mustRefreshForHeights(t5) {
    let e4 = false;
    for (let i9 = 0; i9 < t5.length; i9++) {
      let n22 = t5[i9];
      n22 < 0 ? i9++ : this.heightSamples[Math.floor(n22 * 10)] || (e4 = true, this.heightSamples[Math.floor(n22 * 10)] = true);
    }
    return e4;
  }
  refresh(t5, e4, i9, n22, o4, r2) {
    let l11 = As2.indexOf(t5) > -1, a2 = Math.abs(e4 - this.lineHeight) > 0.3 || this.lineWrapping != l11 || Math.abs(i9 - this.charWidth) > 0.1;
    if (this.lineWrapping = l11, this.lineHeight = e4, this.charWidth = i9, this.textHeight = n22, this.lineLength = o4, a2) {
      this.heightSamples = {};
      for (let h3 = 0; h3 < r2.length; h3++) {
        let c4 = r2[h3];
        c4 < 0 ? h3++ : this.heightSamples[Math.floor(c4 * 10)] = true;
      }
    }
    return a2;
  }
};
var Be7 = class {
  constructor(t5, e4) {
    this.from = t5, this.heights = e4, this.index = 0;
  }
  get more() {
    return this.index < this.heights.length;
  }
};
var _8 = class s79 {
  constructor(t5, e4, i9, n22, o4) {
    this.from = t5, this.length = e4, this.top = i9, this.height = n22, this._content = o4;
  }
  get type() {
    return typeof this._content == "number" ? P8.Text : Array.isArray(this._content) ? this._content : this._content.type;
  }
  get to() {
    return this.from + this.length;
  }
  get bottom() {
    return this.top + this.height;
  }
  get widget() {
    return this._content instanceof mt4 ? this._content.widget : null;
  }
  get widgetLineBreaks() {
    return typeof this._content == "number" ? this._content : 0;
  }
  join(t5) {
    let e4 = (Array.isArray(this._content) ? this._content : [
      this
    ]).concat(Array.isArray(t5._content) ? t5._content : [
      t5
    ]);
    return new s79(this.from, this.length + t5.length, this.top, this.height + t5.height, e4);
  }
};
var D7 = function(s99) {
  return s99[s99.ByPos = 0] = "ByPos", s99[s99.ByHeight = 1] = "ByHeight", s99[s99.ByPosNoHeight = 2] = "ByPosNoHeight", s99;
}(D7 || (D7 = {}));
var ye7 = 1e-3;
var F8 = class s80 {
  constructor(t5, e4, i9 = 2) {
    this.length = t5, this.height = e4, this.flags = i9;
  }
  get outdated() {
    return (this.flags & 2) > 0;
  }
  set outdated(t5) {
    this.flags = (t5 ? 2 : 0) | this.flags & -3;
  }
  setHeight(t5) {
    this.height != t5 && (Math.abs(this.height - t5) > ye7 && (wt4 = true), this.height = t5);
  }
  replace(t5, e4, i9) {
    return s80.of(i9);
  }
  decomposeLeft(t5, e4) {
    e4.push(this);
  }
  decomposeRight(t5, e4) {
    e4.push(this);
  }
  applyChanges(t5, e4, i9, n22) {
    let o4 = this, r2 = i9.doc;
    for (let l11 = n22.length - 1; l11 >= 0; l11--) {
      let { fromA: a2, toA: h3, fromB: c4, toB: f2 } = n22[l11], d5 = o4.lineAt(a2, D7.ByPosNoHeight, i9.setDoc(e4), 0, 0), u5 = d5.to >= h3 ? d5 : o4.lineAt(h3, D7.ByPosNoHeight, i9, 0, 0);
      for (f2 += u5.to - h3, h3 = u5.to; l11 > 0 && d5.from <= n22[l11 - 1].toA; ) a2 = n22[l11 - 1].fromA, c4 = n22[l11 - 1].fromB, l11--, a2 < d5.from && (d5 = o4.lineAt(a2, D7.ByPosNoHeight, i9, 0, 0));
      c4 += d5.from - a2, a2 = d5.from;
      let p5 = Ti2.build(i9.setDoc(r2), t5, c4, f2);
      o4 = Ee6(o4, o4.replace(a2, h3, p5));
    }
    return o4.updateHeight(i9, 0);
  }
  static empty() {
    return new I8(0, 0, 0);
  }
  static of(t5) {
    if (t5.length == 1) return t5[0];
    let e4 = 0, i9 = t5.length, n22 = 0, o4 = 0;
    for (; ; ) if (e4 == i9) if (n22 > o4 * 2) {
      let l11 = t5[e4 - 1];
      l11.break ? t5.splice(--e4, 1, l11.left, null, l11.right) : t5.splice(--e4, 1, l11.left, l11.right), i9 += 1 + l11.break, n22 -= l11.size;
    } else if (o4 > n22 * 2) {
      let l11 = t5[i9];
      l11.break ? t5.splice(i9, 1, l11.left, null, l11.right) : t5.splice(i9, 1, l11.left, l11.right), i9 += 2 + l11.break, o4 -= l11.size;
    } else break;
    else if (n22 < o4) {
      let l11 = t5[e4++];
      l11 && (n22 += l11.size);
    } else {
      let l11 = t5[--i9];
      l11 && (o4 += l11.size);
    }
    let r2 = 0;
    return t5[e4 - 1] == null ? (r2 = 1, e4--) : t5[e4] == null && (r2 = 1, i9++), new Ai2(s80.of(t5.slice(0, e4)), r2, s80.of(t5.slice(i9)));
  }
};
function Ee6(s99, t5) {
  return s99 == t5 ? s99 : (s99.constructor != t5.constructor && (wt4 = true), t5);
}
F8.prototype.size = 1;
var cr2 = T8.replace({});
var He5 = class extends F8 {
  constructor(t5, e4, i9) {
    super(t5, e4), this.deco = i9, this.spaceAbove = 0;
  }
  mainBlock(t5, e4) {
    return new _8(e4, this.length, t5 + this.spaceAbove, this.height - this.spaceAbove, this.deco || 0);
  }
  blockAt(t5, e4, i9, n22) {
    return this.spaceAbove && t5 < i9 + this.spaceAbove ? new _8(n22, 0, i9, this.spaceAbove, cr2) : this.mainBlock(i9, n22);
  }
  lineAt(t5, e4, i9, n22, o4) {
    let r2 = this.mainBlock(n22, o4);
    return this.spaceAbove ? this.blockAt(0, i9, n22, o4).join(r2) : r2;
  }
  forEachLine(t5, e4, i9, n22, o4, r2) {
    t5 <= o4 + this.length && e4 >= o4 && r2(this.lineAt(0, D7.ByPos, i9, n22, o4));
  }
  setMeasuredHeight(t5) {
    let e4 = t5.heights[t5.index++];
    e4 < 0 ? (this.spaceAbove = -e4, e4 = t5.heights[t5.index++]) : this.spaceAbove = 0, this.setHeight(e4);
  }
  updateHeight(t5, e4 = 0, i9 = false, n22) {
    return n22 && n22.from <= e4 && n22.more && this.setMeasuredHeight(n22), this.outdated = false, this;
  }
  toString() {
    return `block(${this.length})`;
  }
};
var I8 = class s81 extends He5 {
  constructor(t5, e4, i9) {
    super(t5, e4, null), this.collapsed = 0, this.widgetHeight = 0, this.breaks = 0, this.spaceAbove = i9;
  }
  mainBlock(t5, e4) {
    return new _8(e4, this.length, t5 + this.spaceAbove, this.height - this.spaceAbove, this.breaks);
  }
  replace(t5, e4, i9) {
    let n22 = i9[0];
    return i9.length == 1 && (n22 instanceof s81 || n22 instanceof ht6 && n22.flags & 4) && Math.abs(this.length - n22.length) < 10 ? (n22 instanceof ht6 ? n22 = new s81(n22.length, this.height, this.spaceAbove) : n22.height = this.height, this.outdated || (n22.outdated = false), n22) : F8.of(i9);
  }
  updateHeight(t5, e4 = 0, i9 = false, n22) {
    return n22 && n22.from <= e4 && n22.more ? this.setMeasuredHeight(n22) : (i9 || this.outdated) && (this.spaceAbove = 0, this.setHeight(Math.max(this.widgetHeight, t5.heightForLine(this.length - this.collapsed)) + this.breaks * t5.lineHeight)), this.outdated = false, this;
  }
  toString() {
    return `line(${this.length}${this.collapsed ? -this.collapsed : ""}${this.widgetHeight ? ":" + this.widgetHeight : ""})`;
  }
};
var ht6 = class s82 extends F8 {
  constructor(t5) {
    super(t5, 0);
  }
  heightMetrics(t5, e4) {
    let i9 = t5.doc.lineAt(e4).number, n22 = t5.doc.lineAt(e4 + this.length).number, o4 = n22 - i9 + 1, r2, l11 = 0;
    if (t5.lineWrapping) {
      let a2 = Math.min(this.height, t5.lineHeight * o4);
      r2 = a2 / o4, this.length > o4 + 1 && (l11 = (this.height - a2) / (this.length - o4 - 1));
    } else r2 = this.height / o4;
    return {
      firstLine: i9,
      lastLine: n22,
      perLine: r2,
      perChar: l11
    };
  }
  blockAt(t5, e4, i9, n22) {
    let { firstLine: o4, lastLine: r2, perLine: l11, perChar: a2 } = this.heightMetrics(e4, n22);
    if (e4.lineWrapping) {
      let h3 = n22 + (t5 < e4.lineHeight ? 0 : Math.round(Math.max(0, Math.min(1, (t5 - i9) / this.height)) * this.length)), c4 = e4.doc.lineAt(h3), f2 = l11 + c4.length * a2, d5 = Math.max(i9, t5 - f2 / 2);
      return new _8(c4.from, c4.length, d5, f2, 0);
    } else {
      let h3 = Math.max(0, Math.min(r2 - o4, Math.floor((t5 - i9) / l11))), { from: c4, length: f2 } = e4.doc.line(o4 + h3);
      return new _8(c4, f2, i9 + l11 * h3, l11, 0);
    }
  }
  lineAt(t5, e4, i9, n22, o4) {
    if (e4 == D7.ByHeight) return this.blockAt(t5, i9, n22, o4);
    if (e4 == D7.ByPosNoHeight) {
      let { from: u5, to: p5 } = i9.doc.lineAt(t5);
      return new _8(u5, p5 - u5, 0, 0, 0);
    }
    let { firstLine: r2, perLine: l11, perChar: a2 } = this.heightMetrics(i9, o4), h3 = i9.doc.lineAt(t5), c4 = l11 + h3.length * a2, f2 = h3.number - r2, d5 = n22 + l11 * f2 + a2 * (h3.from - o4 - f2);
    return new _8(h3.from, h3.length, Math.max(n22, Math.min(d5, n22 + this.height - c4)), c4, 0);
  }
  forEachLine(t5, e4, i9, n22, o4, r2) {
    t5 = Math.max(t5, o4), e4 = Math.min(e4, o4 + this.length);
    let { firstLine: l11, perLine: a2, perChar: h3 } = this.heightMetrics(i9, o4);
    for (let c4 = t5, f2 = n22; c4 <= e4; ) {
      let d5 = i9.doc.lineAt(c4);
      if (c4 == t5) {
        let p5 = d5.number - l11;
        f2 += a2 * p5 + h3 * (t5 - o4 - p5);
      }
      let u5 = a2 + h3 * d5.length;
      r2(new _8(d5.from, d5.length, f2, u5, 0)), f2 += u5, c4 = d5.to + 1;
    }
  }
  replace(t5, e4, i9) {
    let n22 = this.length - e4;
    if (n22 > 0) {
      let o4 = i9[i9.length - 1];
      o4 instanceof s82 ? i9[i9.length - 1] = new s82(o4.length + n22) : i9.push(null, new s82(n22 - 1));
    }
    if (t5 > 0) {
      let o4 = i9[0];
      o4 instanceof s82 ? i9[0] = new s82(t5 + o4.length) : i9.unshift(new s82(t5 - 1), null);
    }
    return F8.of(i9);
  }
  decomposeLeft(t5, e4) {
    e4.push(new s82(t5 - 1), null);
  }
  decomposeRight(t5, e4) {
    e4.push(null, new s82(this.length - t5 - 1));
  }
  updateHeight(t5, e4 = 0, i9 = false, n22) {
    let o4 = e4 + this.length;
    if (n22 && n22.from <= e4 + this.length && n22.more) {
      let r2 = [], l11 = Math.max(e4, n22.from), a2 = -1;
      for (n22.from > e4 && r2.push(new s82(n22.from - e4 - 1).updateHeight(t5, e4)); l11 <= o4 && n22.more; ) {
        let c4 = t5.doc.lineAt(l11).length;
        r2.length && r2.push(null);
        let f2 = n22.heights[n22.index++], d5 = 0;
        f2 < 0 && (d5 = -f2, f2 = n22.heights[n22.index++]), a2 == -1 ? a2 = f2 : Math.abs(f2 - a2) >= ye7 && (a2 = -2);
        let u5 = new I8(c4, f2, d5);
        u5.outdated = false, r2.push(u5), l11 += c4 + 1;
      }
      l11 <= o4 && r2.push(null, new s82(o4 - l11).updateHeight(t5, l11));
      let h3 = F8.of(r2);
      return (a2 < 0 || Math.abs(h3.height - this.height) >= ye7 || Math.abs(a2 - this.heightMetrics(t5, e4).perLine) >= ye7) && (wt4 = true), Ee6(this, h3);
    } else (i9 || this.outdated) && (this.setHeight(t5.heightForGap(e4, e4 + this.length)), this.outdated = false);
    return this;
  }
  toString() {
    return `gap(${this.length})`;
  }
};
var Ai2 = class extends F8 {
  constructor(t5, e4, i9) {
    super(t5.length + e4 + i9.length, t5.height + i9.height, e4 | (t5.outdated || i9.outdated ? 2 : 0)), this.left = t5, this.right = i9, this.size = t5.size + i9.size;
  }
  get break() {
    return this.flags & 1;
  }
  blockAt(t5, e4, i9, n22) {
    let o4 = i9 + this.left.height;
    return t5 < o4 ? this.left.blockAt(t5, e4, i9, n22) : this.right.blockAt(t5, e4, o4, n22 + this.left.length + this.break);
  }
  lineAt(t5, e4, i9, n22, o4) {
    let r2 = n22 + this.left.height, l11 = o4 + this.left.length + this.break, a2 = e4 == D7.ByHeight ? t5 < r2 : t5 < l11, h3 = a2 ? this.left.lineAt(t5, e4, i9, n22, o4) : this.right.lineAt(t5, e4, i9, r2, l11);
    if (this.break || (a2 ? h3.to < l11 : h3.from > l11)) return h3;
    let c4 = e4 == D7.ByPosNoHeight ? D7.ByPosNoHeight : D7.ByPos;
    return a2 ? h3.join(this.right.lineAt(l11, c4, i9, r2, l11)) : this.left.lineAt(l11, c4, i9, n22, o4).join(h3);
  }
  forEachLine(t5, e4, i9, n22, o4, r2) {
    let l11 = n22 + this.left.height, a2 = o4 + this.left.length + this.break;
    if (this.break) t5 < a2 && this.left.forEachLine(t5, e4, i9, n22, o4, r2), e4 >= a2 && this.right.forEachLine(t5, e4, i9, l11, a2, r2);
    else {
      let h3 = this.lineAt(a2, D7.ByPos, i9, n22, o4);
      t5 < h3.from && this.left.forEachLine(t5, h3.from - 1, i9, n22, o4, r2), h3.to >= t5 && h3.from <= e4 && r2(h3), e4 > h3.to && this.right.forEachLine(h3.to + 1, e4, i9, l11, a2, r2);
    }
  }
  replace(t5, e4, i9) {
    let n22 = this.left.length + this.break;
    if (e4 < n22) return this.balanced(this.left.replace(t5, e4, i9), this.right);
    if (t5 > this.left.length) return this.balanced(this.left, this.right.replace(t5 - n22, e4 - n22, i9));
    let o4 = [];
    t5 > 0 && this.decomposeLeft(t5, o4);
    let r2 = o4.length;
    for (let l11 of i9) o4.push(l11);
    if (t5 > 0 && Ts2(o4, r2 - 1), e4 < this.length) {
      let l11 = o4.length;
      this.decomposeRight(e4, o4), Ts2(o4, l11);
    }
    return F8.of(o4);
  }
  decomposeLeft(t5, e4) {
    let i9 = this.left.length;
    if (t5 <= i9) return this.left.decomposeLeft(t5, e4);
    e4.push(this.left), this.break && (i9++, t5 >= i9 && e4.push(null)), t5 > i9 && this.right.decomposeLeft(t5 - i9, e4);
  }
  decomposeRight(t5, e4) {
    let i9 = this.left.length, n22 = i9 + this.break;
    if (t5 >= n22) return this.right.decomposeRight(t5 - n22, e4);
    t5 < i9 && this.left.decomposeRight(t5, e4), this.break && t5 < n22 && e4.push(null), e4.push(this.right);
  }
  balanced(t5, e4) {
    return t5.size > 2 * e4.size || e4.size > 2 * t5.size ? F8.of(this.break ? [
      t5,
      null,
      e4
    ] : [
      t5,
      e4
    ]) : (this.left = Ee6(this.left, t5), this.right = Ee6(this.right, e4), this.setHeight(t5.height + e4.height), this.outdated = t5.outdated || e4.outdated, this.size = t5.size + e4.size, this.length = t5.length + this.break + e4.length, this);
  }
  updateHeight(t5, e4 = 0, i9 = false, n22) {
    let { left: o4, right: r2 } = this, l11 = e4 + o4.length + this.break, a2 = null;
    return n22 && n22.from <= e4 + o4.length && n22.more ? a2 = o4 = o4.updateHeight(t5, e4, i9, n22) : o4.updateHeight(t5, e4, i9), n22 && n22.from <= l11 + r2.length && n22.more ? a2 = r2 = r2.updateHeight(t5, l11, i9, n22) : r2.updateHeight(t5, l11, i9), a2 ? this.balanced(o4, r2) : (this.height = this.left.height + this.right.height, this.outdated = false, this);
  }
  toString() {
    return this.left + (this.break ? " " : "-") + this.right;
  }
};
function Ts2(s99, t5) {
  let e4, i9;
  s99[t5] == null && (e4 = s99[t5 - 1]) instanceof ht6 && (i9 = s99[t5 + 1]) instanceof ht6 && s99.splice(t5 - 1, 3, new ht6(e4.length + 1 + i9.length));
}
var fr2 = 5;
var Ti2 = class s83 {
  constructor(t5, e4) {
    this.pos = t5, this.oracle = e4, this.nodes = [], this.lineStart = -1, this.lineEnd = -1, this.covering = null, this.writtenTo = t5;
  }
  get isCovered() {
    return this.covering && this.nodes[this.nodes.length - 1] == this.covering;
  }
  span(t5, e4) {
    if (this.lineStart > -1) {
      let i9 = Math.min(e4, this.lineEnd), n22 = this.nodes[this.nodes.length - 1];
      n22 instanceof I8 ? n22.length += i9 - this.pos : (i9 > this.pos || !this.isCovered) && this.nodes.push(new I8(i9 - this.pos, -1, 0)), this.writtenTo = i9, e4 > i9 && (this.nodes.push(null), this.writtenTo++, this.lineStart = -1);
    }
    this.pos = e4;
  }
  point(t5, e4, i9) {
    if (t5 < e4 || i9.heightRelevant) {
      let n22 = i9.widget ? i9.widget.estimatedHeight : 0, o4 = i9.widget ? i9.widget.lineBreaks : 0;
      n22 < 0 && (n22 = this.oracle.lineHeight);
      let r2 = e4 - t5;
      i9.block ? this.addBlock(new He5(r2, n22, i9)) : (r2 || o4 || n22 >= fr2) && this.addLineDeco(n22, o4, r2);
    } else e4 > t5 && this.span(t5, e4);
    this.lineEnd > -1 && this.lineEnd < this.pos && (this.lineEnd = this.oracle.doc.lineAt(this.pos).to);
  }
  enterLine() {
    if (this.lineStart > -1) return;
    let { from: t5, to: e4 } = this.oracle.doc.lineAt(this.pos);
    this.lineStart = t5, this.lineEnd = e4, this.writtenTo < t5 && ((this.writtenTo < t5 - 1 || this.nodes[this.nodes.length - 1] == null) && this.nodes.push(this.blankContent(this.writtenTo, t5 - 1)), this.nodes.push(null)), this.pos > t5 && this.nodes.push(new I8(this.pos - t5, -1, 0)), this.writtenTo = this.pos;
  }
  blankContent(t5, e4) {
    let i9 = new ht6(e4 - t5);
    return this.oracle.doc.lineAt(t5).to == e4 && (i9.flags |= 4), i9;
  }
  ensureLine() {
    this.enterLine();
    let t5 = this.nodes.length ? this.nodes[this.nodes.length - 1] : null;
    if (t5 instanceof I8) return t5;
    let e4 = new I8(0, -1, 0);
    return this.nodes.push(e4), e4;
  }
  addBlock(t5) {
    this.enterLine();
    let e4 = t5.deco;
    e4 && e4.startSide > 0 && !this.isCovered && this.ensureLine(), this.nodes.push(t5), this.writtenTo = this.pos = this.pos + t5.length, e4 && e4.endSide > 0 && (this.covering = t5);
  }
  addLineDeco(t5, e4, i9) {
    let n22 = this.ensureLine();
    n22.length += i9, n22.collapsed += i9, n22.widgetHeight = Math.max(n22.widgetHeight, t5), n22.breaks += e4, this.writtenTo = this.pos = this.pos + i9;
  }
  finish(t5) {
    let e4 = this.nodes.length == 0 ? null : this.nodes[this.nodes.length - 1];
    this.lineStart > -1 && !(e4 instanceof I8) && !this.isCovered ? this.nodes.push(new I8(0, -1, 0)) : (this.writtenTo < this.pos || e4 == null) && this.nodes.push(this.blankContent(this.writtenTo, this.pos));
    let i9 = t5;
    for (let n22 of this.nodes) n22 instanceof I8 && n22.updateHeight(this.oracle, i9), i9 += n22 ? n22.length : 1;
    return this.nodes;
  }
  static build(t5, e4, i9, n22) {
    let o4 = new s83(i9, t5);
    return T7.spans(e4, i9, n22, o4, 0), o4.finish(i9);
  }
};
function dr2(s99, t5, e4) {
  let i9 = new Di2();
  return T7.compare(s99, t5, e4, i9, 0), i9.changes;
}
var Di2 = class {
  constructor() {
    this.changes = [];
  }
  compareRange() {
  }
  comparePoint(t5, e4, i9, n22) {
    (t5 < e4 || i9 && i9.heightRelevant || n22 && n22.heightRelevant) && Tt5(t5, e4, this.changes, 5);
  }
};
function ur2(s99, t5) {
  let e4 = s99.getBoundingClientRect(), i9 = s99.ownerDocument, n22 = i9.defaultView || globalThis, o4 = Math.max(0, e4.left), r2 = Math.min(n22.innerWidth, e4.right), l11 = Math.max(0, e4.top), a2 = Math.min(n22.innerHeight, e4.bottom);
  for (let h3 = s99.parentNode; h3 && h3 != i9.body; ) if (h3.nodeType == 1) {
    let c4 = h3, f2 = globalThis.getComputedStyle(c4);
    if ((c4.scrollHeight > c4.clientHeight || c4.scrollWidth > c4.clientWidth) && f2.overflow != "visible") {
      let d5 = c4.getBoundingClientRect();
      o4 = Math.max(o4, d5.left), r2 = Math.min(r2, d5.right), l11 = Math.max(l11, d5.top), a2 = Math.min(h3 == s99.parentNode ? n22.innerHeight : a2, d5.bottom);
    }
    h3 = f2.position == "absolute" || f2.position == "fixed" ? c4.offsetParent : c4.parentNode;
  } else if (h3.nodeType == 11) h3 = h3.host;
  else break;
  return {
    left: o4 - e4.left,
    right: Math.max(o4, r2) - e4.left,
    top: l11 - (e4.top + t5),
    bottom: Math.max(l11, a2) - (e4.top + t5)
  };
}
function pr2(s99) {
  let t5 = s99.getBoundingClientRect(), e4 = s99.ownerDocument.defaultView || globalThis;
  return t5.left < e4.innerWidth && t5.right > 0 && t5.top < e4.innerHeight && t5.bottom > 0;
}
function gr2(s99, t5) {
  let e4 = s99.getBoundingClientRect();
  return {
    left: 0,
    right: e4.right - e4.left,
    top: t5,
    bottom: e4.bottom - (e4.top + t5)
  };
}
var Xt4 = class {
  constructor(t5, e4, i9, n22) {
    this.from = t5, this.to = e4, this.size = i9, this.displaySize = n22;
  }
  static same(t5, e4) {
    if (t5.length != e4.length) return false;
    for (let i9 = 0; i9 < t5.length; i9++) {
      let n22 = t5[i9], o4 = e4[i9];
      if (n22.from != o4.from || n22.to != o4.to || n22.size != o4.size) return false;
    }
    return true;
  }
  draw(t5, e4) {
    return T8.replace({
      widget: new Oi2(this.displaySize * (e4 ? t5.scaleY : t5.scaleX), e4)
    }).range(this.from, this.to);
  }
};
var Oi2 = class extends et4 {
  constructor(t5, e4) {
    super(), this.size = t5, this.vertical = e4;
  }
  eq(t5) {
    return t5.size == this.size && t5.vertical == this.vertical;
  }
  toDOM() {
    let t5 = document.createElement("div");
    return this.vertical ? t5.style.height = this.size + "px" : (t5.style.width = this.size + "px", t5.style.height = "2px", t5.style.display = "inline-block"), t5;
  }
  get estimatedHeight() {
    return this.vertical ? this.size : -1;
  }
};
var Pe8 = class {
  constructor(t5) {
    this.state = t5, this.pixelViewport = {
      left: 0,
      right: globalThis.innerWidth,
      top: 0,
      bottom: 0
    }, this.inView = true, this.paddingTop = 0, this.paddingBottom = 0, this.contentDOMWidth = 0, this.contentDOMHeight = 0, this.editorHeight = 0, this.editorWidth = 0, this.scrollTop = 0, this.scrolledToBottom = false, this.scaleX = 1, this.scaleY = 1, this.scrollAnchorPos = 0, this.scrollAnchorHeight = -1, this.scaler = Ds2, this.scrollTarget = null, this.printing = false, this.mustMeasureContent = true, this.defaultTextDirection = R9.LTR, this.visibleRanges = [], this.mustEnforceCursorAssoc = false;
    let e4 = t5.facet(qe6).some((i9) => typeof i9 != "function" && i9.class == "cm-lineWrapping");
    this.heightOracle = new Re7(e4), this.stateDeco = Os2(t5), this.heightMap = F8.empty().applyChanges(this.stateDeco, m7.empty, this.heightOracle.setDoc(t5.doc), [
      new q8(0, 0, 0, t5.doc.length)
    ]);
    for (let i9 = 0; i9 < 2 && (this.viewport = this.getViewport(0, null), !!this.updateForViewport()); i9++) ;
    this.updateViewportLines(), this.lineGaps = this.ensureLineGaps([]), this.lineGapDeco = T8.set(this.lineGaps.map((i9) => i9.draw(this, false))), this.computeVisibleRanges();
  }
  updateForViewport() {
    let t5 = [
      this.viewport
    ], { main: e4 } = this.state.selection;
    for (let i9 = 0; i9 <= 1; i9++) {
      let n22 = i9 ? e4.head : e4.anchor;
      if (!t5.some(({ from: o4, to: r2 }) => n22 >= o4 && n22 <= r2)) {
        let { from: o4, to: r2 } = this.lineBlockAt(n22);
        t5.push(new Ct5(o4, r2));
      }
    }
    return this.viewports = t5.sort((i9, n22) => i9.from - n22.from), this.updateScaler();
  }
  updateScaler() {
    let t5 = this.scaler;
    return this.scaler = this.heightMap.height <= 7e6 ? Ds2 : new Li2(this.heightOracle, this.heightMap, this.viewports), t5.eq(this.scaler) ? 0 : 2;
  }
  updateViewportLines() {
    this.viewportLines = [], this.heightMap.forEachLine(this.viewport.from, this.viewport.to, this.heightOracle.setDoc(this.state.doc), 0, 0, (t5) => {
      this.viewportLines.push(Vt2(t5, this.scaler));
    });
  }
  update(t5, e4 = null) {
    this.state = t5.state;
    let i9 = this.stateDeco;
    this.stateDeco = Os2(this.state);
    let n22 = t5.changedRanges, o4 = q8.extendWithRanges(n22, dr2(i9, this.stateDeco, t5 ? t5.changes : A8.empty(this.state.doc.length))), r2 = this.heightMap.height, l11 = this.scrolledToBottom ? null : this.scrollAnchorAt(this.scrollTop);
    ki2(), this.heightMap = this.heightMap.applyChanges(this.stateDeco, t5.startState.doc, this.heightOracle.setDoc(this.state.doc), o4), (this.heightMap.height != r2 || wt4) && (t5.flags |= 2), l11 ? (this.scrollAnchorPos = t5.changes.mapPos(l11.from, -1), this.scrollAnchorHeight = l11.top) : (this.scrollAnchorPos = -1, this.scrollAnchorHeight = r2);
    let a2 = o4.length ? this.mapViewport(this.viewport, t5.changes) : this.viewport;
    (e4 && (e4.range.head < a2.from || e4.range.head > a2.to) || !this.viewportIsAppropriate(a2)) && (a2 = this.getViewport(0, e4));
    let h3 = a2.from != this.viewport.from || a2.to != this.viewport.to;
    this.viewport = a2, t5.flags |= this.updateForViewport(), (h3 || !t5.changes.empty || t5.flags & 2) && this.updateViewportLines(), (this.lineGaps.length || this.viewport.to - this.viewport.from > 4e3) && this.updateLineGaps(this.ensureLineGaps(this.mapLineGaps(this.lineGaps, t5.changes))), t5.flags |= this.computeVisibleRanges(t5.changes), e4 && (this.scrollTarget = e4), !this.mustEnforceCursorAssoc && (t5.selectionSet || t5.focusChanged) && t5.view.lineWrapping && t5.state.selection.main.empty && t5.state.selection.main.assoc && !t5.state.facet(bn2) && (this.mustEnforceCursorAssoc = true);
  }
  measure(t5) {
    let e4 = t5.contentDOM, i9 = globalThis.getComputedStyle(e4), n22 = this.heightOracle, o4 = i9.whiteSpace;
    this.defaultTextDirection = i9.direction == "rtl" ? R9.RTL : R9.LTR;
    let r2 = this.heightOracle.mustRefreshForWrapping(o4) || this.mustMeasureContent, l11 = e4.getBoundingClientRect(), a2 = r2 || this.mustMeasureContent || this.contentDOMHeight != l11.height;
    this.contentDOMHeight = l11.height, this.mustMeasureContent = false;
    let h3 = 0, c4 = 0;
    if (l11.width && l11.height) {
      let { scaleX: A11, scaleY: v8 } = Qs2(e4, l11);
      (A11 > 5e-3 && Math.abs(this.scaleX - A11) > 5e-3 || v8 > 5e-3 && Math.abs(this.scaleY - v8) > 5e-3) && (this.scaleX = A11, this.scaleY = v8, h3 |= 16, r2 = a2 = true);
    }
    let f2 = (parseInt(i9.paddingTop) || 0) * this.scaleY, d5 = (parseInt(i9.paddingBottom) || 0) * this.scaleY;
    (this.paddingTop != f2 || this.paddingBottom != d5) && (this.paddingTop = f2, this.paddingBottom = d5, h3 |= 18), this.editorWidth != t5.scrollDOM.clientWidth && (n22.lineWrapping && (a2 = true), this.editorWidth = t5.scrollDOM.clientWidth, h3 |= 16);
    let u5 = t5.scrollDOM.scrollTop * this.scaleY;
    this.scrollTop != u5 && (this.scrollAnchorHeight = -1, this.scrollTop = u5), this.scrolledToBottom = Zs2(t5.scrollDOM);
    let p5 = (this.printing ? gr2 : ur2)(e4, this.paddingTop), g6 = p5.top - this.pixelViewport.top, m9 = p5.bottom - this.pixelViewport.bottom;
    this.pixelViewport = p5;
    let b9 = this.pixelViewport.bottom > this.pixelViewport.top && this.pixelViewport.right > this.pixelViewport.left;
    if (b9 != this.inView && (this.inView = b9, b9 && (a2 = true)), !this.inView && !this.scrollTarget && !pr2(t5.dom)) return 0;
    let w11 = l11.width;
    if ((this.contentDOMWidth != w11 || this.editorHeight != t5.scrollDOM.clientHeight) && (this.contentDOMWidth = l11.width, this.editorHeight = t5.scrollDOM.clientHeight, h3 |= 16), a2) {
      let A11 = t5.docView.measureVisibleLineHeights(this.viewport);
      if (n22.mustRefreshForHeights(A11) && (r2 = true), r2 || n22.lineWrapping && Math.abs(w11 - this.contentDOMWidth) > n22.charWidth) {
        let { lineHeight: v8, charWidth: x11, textHeight: L10 } = t5.docView.measureTextSize();
        r2 = v8 > 0 && n22.refresh(o4, v8, x11, L10, Math.max(5, w11 / x11), A11), r2 && (t5.docView.minWidth = 0, h3 |= 16);
      }
      g6 > 0 && m9 > 0 ? c4 = Math.max(g6, m9) : g6 < 0 && m9 < 0 && (c4 = Math.min(g6, m9)), ki2();
      for (let v8 of this.viewports) {
        let x11 = v8.from == this.viewport.from ? A11 : t5.docView.measureVisibleLineHeights(v8);
        this.heightMap = (r2 ? F8.empty().applyChanges(this.stateDeco, m7.empty, this.heightOracle, [
          new q8(0, 0, 0, t5.state.doc.length)
        ]) : this.heightMap).updateHeight(n22, 0, r2, new Be7(v8.from, x11));
      }
      wt4 && (h3 |= 2);
    }
    let M14 = !this.viewportIsAppropriate(this.viewport, c4) || this.scrollTarget && (this.scrollTarget.range.head < this.viewport.from || this.scrollTarget.range.head > this.viewport.to);
    return M14 && (h3 & 2 && (h3 |= this.updateScaler()), this.viewport = this.getViewport(c4, this.scrollTarget), h3 |= this.updateForViewport()), (h3 & 2 || M14) && this.updateViewportLines(), (this.lineGaps.length || this.viewport.to - this.viewport.from > 4e3) && this.updateLineGaps(this.ensureLineGaps(r2 ? [] : this.lineGaps, t5)), h3 |= this.computeVisibleRanges(), this.mustEnforceCursorAssoc && (this.mustEnforceCursorAssoc = false, t5.docView.enforceCursorAssoc()), h3;
  }
  get visibleTop() {
    return this.scaler.fromDOM(this.pixelViewport.top);
  }
  get visibleBottom() {
    return this.scaler.fromDOM(this.pixelViewport.bottom);
  }
  getViewport(t5, e4) {
    let i9 = 0.5 - Math.max(-0.5, Math.min(0.5, t5 / 1e3 / 2)), n22 = this.heightMap, o4 = this.heightOracle, { visibleTop: r2, visibleBottom: l11 } = this, a2 = new Ct5(n22.lineAt(r2 - i9 * 1e3, D7.ByHeight, o4, 0, 0).from, n22.lineAt(l11 + (1 - i9) * 1e3, D7.ByHeight, o4, 0, 0).to);
    if (e4) {
      let { head: h3 } = e4.range;
      if (h3 < a2.from || h3 > a2.to) {
        let c4 = Math.min(this.editorHeight, this.pixelViewport.bottom - this.pixelViewport.top), f2 = n22.lineAt(h3, D7.ByPos, o4, 0, 0), d5;
        e4.y == "center" ? d5 = (f2.top + f2.bottom) / 2 - c4 / 2 : e4.y == "start" || e4.y == "nearest" && h3 < a2.from ? d5 = f2.top : d5 = f2.bottom - c4, a2 = new Ct5(n22.lineAt(d5 - 1e3 / 2, D7.ByHeight, o4, 0, 0).from, n22.lineAt(d5 + c4 + 1e3 / 2, D7.ByHeight, o4, 0, 0).to);
      }
    }
    return a2;
  }
  mapViewport(t5, e4) {
    let i9 = e4.mapPos(t5.from, -1), n22 = e4.mapPos(t5.to, 1);
    return new Ct5(this.heightMap.lineAt(i9, D7.ByPos, this.heightOracle, 0, 0).from, this.heightMap.lineAt(n22, D7.ByPos, this.heightOracle, 0, 0).to);
  }
  viewportIsAppropriate({ from: t5, to: e4 }, i9 = 0) {
    if (!this.inView) return true;
    let { top: n22 } = this.heightMap.lineAt(t5, D7.ByPos, this.heightOracle, 0, 0), { bottom: o4 } = this.heightMap.lineAt(e4, D7.ByPos, this.heightOracle, 0, 0), { visibleTop: r2, visibleBottom: l11 } = this;
    return (t5 == 0 || n22 <= r2 - Math.max(10, Math.min(-i9, 250))) && (e4 == this.state.doc.length || o4 >= l11 + Math.max(10, Math.min(i9, 250))) && n22 > r2 - 2 * 1e3 && o4 < l11 + 2 * 1e3;
  }
  mapLineGaps(t5, e4) {
    if (!t5.length || e4.empty) return t5;
    let i9 = [];
    for (let n22 of t5) e4.touchesRange(n22.from, n22.to) || i9.push(new Xt4(e4.mapPos(n22.from), e4.mapPos(n22.to), n22.size, n22.displaySize));
    return i9;
  }
  ensureLineGaps(t5, e4) {
    let i9 = this.heightOracle.lineWrapping, n22 = i9 ? 1e4 : 2e3, o4 = n22 >> 1, r2 = n22 << 1;
    if (this.defaultTextDirection != R9.LTR && !i9) return [];
    let l11 = [], a2 = (c4, f2, d5, u5) => {
      if (f2 - c4 < o4) return;
      let p5 = this.state.selection.main, g6 = [
        p5.from
      ];
      p5.empty || g6.push(p5.to);
      for (let b9 of g6) if (b9 > c4 && b9 < f2) {
        a2(c4, b9 - 10, d5, u5), a2(b9 + 10, f2, d5, u5);
        return;
      }
      let m9 = br2(t5, (b9) => b9.from >= d5.from && b9.to <= d5.to && Math.abs(b9.from - c4) < o4 && Math.abs(b9.to - f2) < o4 && !g6.some((w11) => b9.from < w11 && b9.to > w11));
      if (!m9) {
        if (f2 < d5.to && e4 && i9 && e4.visibleRanges.some((M14) => M14.from <= f2 && M14.to >= f2)) {
          let M14 = e4.moveToLineBoundary(x8.cursor(f2), false, true).head;
          M14 > c4 && (f2 = M14);
        }
        let b9 = this.gapSize(d5, c4, f2, u5), w11 = i9 || b9 < 2e6 ? b9 : 2e6;
        m9 = new Xt4(c4, f2, b9, w11);
      }
      l11.push(m9);
    }, h3 = (c4) => {
      if (c4.length < r2 || c4.type != P8.Text) return;
      let f2 = mr2(c4.from, c4.to, this.stateDeco);
      if (f2.total < r2) return;
      let d5 = this.scrollTarget ? this.scrollTarget.range.head : null, u5, p5;
      if (i9) {
        let g6 = n22 / this.heightOracle.lineLength * this.heightOracle.lineHeight, m9, b9;
        if (d5 != null) {
          let w11 = de8(f2, d5), M14 = ((this.visibleBottom - this.visibleTop) / 2 + g6) / c4.height;
          m9 = w11 - M14, b9 = w11 + M14;
        } else m9 = (this.visibleTop - c4.top - g6) / c4.height, b9 = (this.visibleBottom - c4.top + g6) / c4.height;
        u5 = fe7(f2, m9), p5 = fe7(f2, b9);
      } else {
        let g6 = f2.total * this.heightOracle.charWidth, m9 = n22 * this.heightOracle.charWidth, b9 = 0;
        if (g6 > 2e6) for (let x11 of t5) x11.from >= c4.from && x11.from < c4.to && x11.size != x11.displaySize && x11.from * this.heightOracle.charWidth + b9 < this.pixelViewport.left && (b9 = x11.size - x11.displaySize);
        let w11 = this.pixelViewport.left + b9, M14 = this.pixelViewport.right + b9, A11, v8;
        if (d5 != null) {
          let x11 = de8(f2, d5), L10 = ((M14 - w11) / 2 + m9) / g6;
          A11 = x11 - L10, v8 = x11 + L10;
        } else A11 = (w11 - m9) / g6, v8 = (M14 + m9) / g6;
        u5 = fe7(f2, A11), p5 = fe7(f2, v8);
      }
      u5 > c4.from && a2(c4.from, u5, c4, f2), p5 < c4.to && a2(p5, c4.to, c4, f2);
    };
    for (let c4 of this.viewportLines) Array.isArray(c4.type) ? c4.type.forEach(h3) : h3(c4);
    return l11;
  }
  gapSize(t5, e4, i9, n22) {
    let o4 = de8(n22, i9) - de8(n22, e4);
    return this.heightOracle.lineWrapping ? t5.height * o4 : n22.total * this.heightOracle.charWidth * o4;
  }
  updateLineGaps(t5) {
    Xt4.same(t5, this.lineGaps) || (this.lineGaps = t5, this.lineGapDeco = T8.set(t5.map((e4) => e4.draw(this, this.heightOracle.lineWrapping))));
  }
  computeVisibleRanges(t5) {
    let e4 = this.stateDeco;
    this.lineGaps.length && (e4 = e4.concat(this.lineGapDeco));
    let i9 = [];
    T7.spans(e4, this.viewport.from, this.viewport.to, {
      span(o4, r2) {
        i9.push({
          from: o4,
          to: r2
        });
      },
      point() {
      }
    }, 20);
    let n22 = 0;
    if (i9.length != this.visibleRanges.length) n22 = 12;
    else for (let o4 = 0; o4 < i9.length && !(n22 & 8); o4++) {
      let r2 = this.visibleRanges[o4], l11 = i9[o4];
      (r2.from != l11.from || r2.to != l11.to) && (n22 |= 4, t5 && t5.mapPos(r2.from, -1) == l11.from && t5.mapPos(r2.to, 1) == l11.to || (n22 |= 8));
    }
    return this.visibleRanges = i9, n22;
  }
  lineBlockAt(t5) {
    return t5 >= this.viewport.from && t5 <= this.viewport.to && this.viewportLines.find((e4) => e4.from <= t5 && e4.to >= t5) || Vt2(this.heightMap.lineAt(t5, D7.ByPos, this.heightOracle, 0, 0), this.scaler);
  }
  lineBlockAtHeight(t5) {
    return t5 >= this.viewportLines[0].top && t5 <= this.viewportLines[this.viewportLines.length - 1].bottom && this.viewportLines.find((e4) => e4.top <= t5 && e4.bottom >= t5) || Vt2(this.heightMap.lineAt(this.scaler.fromDOM(t5), D7.ByHeight, this.heightOracle, 0, 0), this.scaler);
  }
  scrollAnchorAt(t5) {
    let e4 = this.lineBlockAtHeight(t5 + 8);
    return e4.from >= this.viewport.from || this.viewportLines[0].top - t5 > 200 ? e4 : this.viewportLines[0];
  }
  elementAtHeight(t5) {
    return Vt2(this.heightMap.blockAt(this.scaler.fromDOM(t5), this.heightOracle, 0, 0), this.scaler);
  }
  get docHeight() {
    return this.scaler.toDOM(this.heightMap.height);
  }
  get contentHeight() {
    return this.docHeight + this.paddingTop + this.paddingBottom;
  }
};
var Ct5 = class {
  constructor(t5, e4) {
    this.from = t5, this.to = e4;
  }
};
function mr2(s99, t5, e4) {
  let i9 = [], n22 = s99, o4 = 0;
  return T7.spans(e4, s99, t5, {
    span() {
    },
    point(r2, l11) {
      r2 > n22 && (i9.push({
        from: n22,
        to: r2
      }), o4 += r2 - n22), n22 = l11;
    }
  }, 20), n22 < t5 && (i9.push({
    from: n22,
    to: t5
  }), o4 += t5 - n22), {
    total: o4,
    ranges: i9
  };
}
function fe7({ total: s99, ranges: t5 }, e4) {
  if (e4 <= 0) return t5[0].from;
  if (e4 >= 1) return t5[t5.length - 1].to;
  let i9 = Math.floor(s99 * e4);
  for (let n22 = 0; ; n22++) {
    let { from: o4, to: r2 } = t5[n22], l11 = r2 - o4;
    if (i9 <= l11) return o4 + i9;
    i9 -= l11;
  }
}
function de8(s99, t5) {
  let e4 = 0;
  for (let { from: i9, to: n22 } of s99.ranges) {
    if (t5 <= n22) {
      e4 += t5 - i9;
      break;
    }
    e4 += n22 - i9;
  }
  return e4 / s99.total;
}
function br2(s99, t5) {
  for (let e4 of s99) if (t5(e4)) return e4;
}
var Ds2 = {
  toDOM(s99) {
    return s99;
  },
  fromDOM(s99) {
    return s99;
  },
  scale: 1,
  eq(s99) {
    return s99 == this;
  }
};
function Os2(s99) {
  let t5 = s99.facet(Ke5).filter((i9) => typeof i9 != "function"), e4 = s99.facet(ns2).filter((i9) => typeof i9 != "function");
  return e4.length && t5.push(T7.join(e4)), t5;
}
var Li2 = class s84 {
  constructor(t5, e4, i9) {
    let n22 = 0, o4 = 0, r2 = 0;
    this.viewports = i9.map(({ from: l11, to: a2 }) => {
      let h3 = e4.lineAt(l11, D7.ByPos, t5, 0, 0).top, c4 = e4.lineAt(a2, D7.ByPos, t5, 0, 0).bottom;
      return n22 += c4 - h3, {
        from: l11,
        to: a2,
        top: h3,
        bottom: c4,
        domTop: 0,
        domBottom: 0
      };
    }), this.scale = (7e6 - n22) / (e4.height - n22);
    for (let l11 of this.viewports) l11.domTop = r2 + (l11.top - o4) * this.scale, r2 = l11.domBottom = l11.domTop + (l11.bottom - l11.top), o4 = l11.bottom;
  }
  toDOM(t5) {
    for (let e4 = 0, i9 = 0, n22 = 0; ; e4++) {
      let o4 = e4 < this.viewports.length ? this.viewports[e4] : null;
      if (!o4 || t5 < o4.top) return n22 + (t5 - i9) * this.scale;
      if (t5 <= o4.bottom) return o4.domTop + (t5 - o4.top);
      i9 = o4.bottom, n22 = o4.domBottom;
    }
  }
  fromDOM(t5) {
    for (let e4 = 0, i9 = 0, n22 = 0; ; e4++) {
      let o4 = e4 < this.viewports.length ? this.viewports[e4] : null;
      if (!o4 || t5 < o4.domTop) return i9 + (t5 - n22) / this.scale;
      if (t5 <= o4.domBottom) return o4.top + (t5 - o4.domTop);
      i9 = o4.bottom, n22 = o4.domBottom;
    }
  }
  eq(t5) {
    return t5 instanceof s84 ? this.scale == t5.scale && this.viewports.length == t5.viewports.length && this.viewports.every((e4, i9) => e4.from == t5.viewports[i9].from && e4.to == t5.viewports[i9].to) : false;
  }
};
function Vt2(s99, t5) {
  if (t5.scale == 1) return s99;
  let e4 = t5.toDOM(s99.top), i9 = t5.toDOM(s99.bottom);
  return new _8(s99.from, s99.length, e4, i9 - e4, Array.isArray(s99._content) ? s99._content.map((n22) => Vt2(n22, t5)) : s99._content);
}
var ue8 = k7.define({
  combine: (s99) => s99.join(" ")
});
var Ri2 = k7.define({
  combine: (s99) => s99.indexOf(true) > -1
});
var Bi2 = T2.newName();
var Fn2 = T2.newName();
var In2 = T2.newName();
var zn2 = {
  "&light": "." + Fn2,
  "&dark": "." + In2
};
function Ei2(s99, t5, e4) {
  return new T2(t5, {
    finish(i9) {
      return /&/.test(i9) ? i9.replace(/&\w*/, (n22) => {
        if (n22 == "&") return s99;
        if (!e4 || !e4[n22]) throw new RangeError(`Unsupported selector: ${n22}`);
        return e4[n22];
      }) : s99 + " " + i9;
    }
  });
}
var yr2 = Ei2("." + Bi2, {
  "&": {
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
    zIndex: 0,
    overflowAnchor: "none"
  },
  ".cm-content": {
    margin: 0,
    flexGrow: 2,
    flexShrink: 0,
    display: "block",
    whiteSpace: "pre",
    wordWrap: "normal",
    boxSizing: "border-box",
    minHeight: "100%",
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
    overflowWrap: "anywhere",
    flexShrink: 1
  },
  "&light .cm-content": {
    caretColor: "black"
  },
  "&dark .cm-content": {
    caretColor: "white"
  },
  ".cm-line": {
    display: "block",
    padding: "0 2px 0 6px"
  },
  ".cm-layer": {
    position: "absolute",
    left: 0,
    top: 0,
    contain: "size style",
    "& > *": {
      position: "absolute"
    }
  },
  "&light .cm-selectionBackground": {
    background: "#d9d9d9"
  },
  "&dark .cm-selectionBackground": {
    background: "#222"
  },
  "&light.cm-focused > .cm-scroller > .cm-selectionLayer .cm-selectionBackground": {
    background: "#d7d4f0"
  },
  "&dark.cm-focused > .cm-scroller > .cm-selectionLayer .cm-selectionBackground": {
    background: "#233"
  },
  ".cm-cursorLayer": {
    pointerEvents: "none"
  },
  "&.cm-focused > .cm-scroller > .cm-cursorLayer": {
    animation: "steps(1) cm-blink 1.2s infinite"
  },
  "@keyframes cm-blink": {
    "0%": {},
    "50%": {
      opacity: 0
    },
    "100%": {}
  },
  "@keyframes cm-blink2": {
    "0%": {},
    "50%": {
      opacity: 0
    },
    "100%": {}
  },
  ".cm-cursor, .cm-dropCursor": {
    borderLeft: "1.2px solid black",
    marginLeft: "-0.6px",
    pointerEvents: "none"
  },
  ".cm-cursor": {
    display: "none"
  },
  "&dark .cm-cursor": {
    borderLeftColor: "#ddd"
  },
  ".cm-dropCursor": {
    position: "absolute"
  },
  "&.cm-focused > .cm-scroller > .cm-cursorLayer .cm-cursor": {
    display: "block"
  },
  ".cm-iso": {
    unicodeBidi: "isolate"
  },
  ".cm-announced": {
    position: "fixed",
    top: "-10000px"
  },
  "@media print": {
    ".cm-announced": {
      display: "none"
    }
  },
  "&light .cm-activeLine": {
    backgroundColor: "#cceeff44"
  },
  "&dark .cm-activeLine": {
    backgroundColor: "#99eeff33"
  },
  "&light .cm-specialChar": {
    color: "red"
  },
  "&dark .cm-specialChar": {
    color: "#f78"
  },
  ".cm-gutters": {
    flexShrink: 0,
    display: "flex",
    height: "100%",
    boxSizing: "border-box",
    zIndex: 200
  },
  ".cm-gutters-before": {
    insetInlineStart: 0
  },
  ".cm-gutters-after": {
    insetInlineEnd: 0
  },
  "&light .cm-gutters": {
    backgroundColor: "#f5f5f5",
    color: "#6c6c6c",
    border: "0px solid #ddd",
    "&.cm-gutters-before": {
      borderRightWidth: "1px"
    },
    "&.cm-gutters-after": {
      borderLeftWidth: "1px"
    }
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
    right: 0,
    zIndex: 300
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
  ".cm-dialog": {
    padding: "2px 19px 4px 6px",
    position: "relative",
    "& label": {
      fontSize: "80%"
    }
  },
  ".cm-dialog-close": {
    position: "absolute",
    top: "3px",
    right: "4px",
    backgroundColor: "inherit",
    border: "none",
    font: "inherit",
    fontSize: "14px",
    padding: "0"
  },
  ".cm-tab": {
    display: "inline-block",
    overflow: "hidden",
    verticalAlign: "bottom"
  },
  ".cm-widgetBuffer": {
    verticalAlign: "text-top",
    height: "1em",
    width: 0,
    display: "inline"
  },
  ".cm-placeholder": {
    color: "#888",
    display: "inline-block",
    verticalAlign: "top",
    userSelect: "none"
  },
  ".cm-highlightSpace": {
    backgroundImage: "radial-gradient(circle at 50% 55%, #aaa 20%, transparent 5%)",
    backgroundPosition: "center"
  },
  ".cm-highlightTab": {
    backgroundImage: `url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="20"><path stroke="%23888" stroke-width="1" fill="none" d="M1 10H196L190 5M190 15L196 10M197 4L197 16"/></svg>')`,
    backgroundSize: "auto 100%",
    backgroundPosition: "right 90%",
    backgroundRepeat: "no-repeat"
  },
  ".cm-trailingSpace": {
    backgroundColor: "#ff332255"
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
}, zn2);
var wr2 = {
  childList: true,
  characterData: true,
  subtree: true,
  attributes: true,
  characterDataOldValue: true
};
var Ue6 = y8.ie && y8.ie_version <= 11;
var Hi2 = class {
  constructor(t5) {
    this.view = t5, this.active = false, this.editContext = null, this.selectionRange = new oi2(), this.selectionChanged = false, this.delayedFlush = -1, this.resizeTimeout = -1, this.queue = [], this.delayedAndroidKey = null, this.flushingAndroidKey = -1, this.lastChange = 0, this.scrollTargets = [], this.intersection = null, this.resizeScroll = null, this.intersecting = false, this.gapIntersection = null, this.gaps = [], this.printQuery = null, this.parentCheck = -1, this.dom = t5.contentDOM, this.observer = new MutationObserver((e4) => {
      for (let i9 of e4) this.queue.push(i9);
      (y8.ie && y8.ie_version <= 11 || y8.ios && t5.composing) && e4.some((i9) => i9.type == "childList" && i9.removedNodes.length || i9.type == "characterData" && i9.oldValue.length > i9.target.nodeValue.length) ? this.flushSoon() : this.flush();
    }), globalThis.EditContext && y8.android && t5.constructor.EDIT_CONTEXT !== false && !(y8.chrome && y8.chrome_version < 126) && (this.editContext = new Pi2(t5), t5.state.facet(tt6) && (t5.contentDOM.editContext = this.editContext.editContext)), Ue6 && (this.onCharData = (e4) => {
      this.queue.push({
        target: e4.target,
        type: "characterData",
        oldValue: e4.prevValue
      }), this.flushSoon();
    }), this.onSelectionChange = this.onSelectionChange.bind(this), this.onResize = this.onResize.bind(this), this.onPrint = this.onPrint.bind(this), this.onScroll = this.onScroll.bind(this), globalThis.matchMedia && (this.printQuery = globalThis.matchMedia("print")), typeof ResizeObserver == "function" && (this.resizeScroll = new ResizeObserver(() => {
      var e4;
      ((e4 = this.view.docView) === null || e4 === void 0 ? void 0 : e4.lastUpdate) < Date.now() - 75 && this.onResize();
    }), this.resizeScroll.observe(t5.scrollDOM)), this.addWindowListeners(this.win = t5.win), this.start(), typeof IntersectionObserver == "function" && (this.intersection = new IntersectionObserver((e4) => {
      this.parentCheck < 0 && (this.parentCheck = setTimeout(this.listenForScroll.bind(this), 1e3)), e4.length > 0 && e4[e4.length - 1].intersectionRatio > 0 != this.intersecting && (this.intersecting = !this.intersecting, this.intersecting != this.view.inView && this.onScrollChanged(document.createEvent("Event")));
    }, {
      threshold: [
        0,
        1e-3
      ]
    }), this.intersection.observe(this.dom), this.gapIntersection = new IntersectionObserver((e4) => {
      e4.length > 0 && e4[e4.length - 1].intersectionRatio > 0 && this.onScrollChanged(document.createEvent("Event"));
    }, {})), this.listenForScroll(), this.readSelectionRange();
  }
  onScrollChanged(t5) {
    this.view.inputState.runHandlers("scroll", t5), this.intersecting && this.view.measure();
  }
  onScroll(t5) {
    this.intersecting && this.flush(false), this.editContext && this.view.requestMeasure(this.editContext.measureReq), this.onScrollChanged(t5);
  }
  onResize() {
    this.resizeTimeout < 0 && (this.resizeTimeout = setTimeout(() => {
      this.resizeTimeout = -1, this.view.requestMeasure();
    }, 50));
  }
  onPrint(t5) {
    (t5.type == "change" || !t5.type) && !t5.matches || (this.view.viewState.printing = true, this.view.measure(), setTimeout(() => {
      this.view.viewState.printing = false, this.view.requestMeasure();
    }, 500));
  }
  updateGaps(t5) {
    if (this.gapIntersection && (t5.length != this.gaps.length || this.gaps.some((e4, i9) => e4 != t5[i9]))) {
      this.gapIntersection.disconnect();
      for (let e4 of t5) this.gapIntersection.observe(e4);
      this.gaps = t5;
    }
  }
  onSelectionChange(t5) {
    let e4 = this.selectionChanged;
    if (!this.readSelectionRange() || this.delayedAndroidKey) return;
    let { view: i9 } = this, n22 = this.selectionRange;
    if (i9.state.facet(tt6) ? i9.root.activeElement != this.dom : !be7(this.dom, n22)) return;
    let o4 = n22.anchorNode && i9.docView.tile.nearest(n22.anchorNode);
    if (o4 && o4.isWidget() && o4.widget.ignoreEvent(t5)) {
      e4 || (this.selectionChanged = false);
      return;
    }
    (y8.ie && y8.ie_version <= 11 || y8.android && y8.chrome) && !i9.state.selection.main.empty && n22.focusNode && qt3(n22.focusNode, n22.focusOffset, n22.anchorNode, n22.anchorOffset) ? this.flushSoon() : this.flush(false);
  }
  readSelectionRange() {
    let { view: t5 } = this, e4 = Jt3(t5.root);
    if (!e4) return false;
    let i9 = y8.safari && t5.root.nodeType == 11 && t5.root.activeElement == this.dom && xr2(this.view, e4) || e4;
    if (!i9 || this.selectionRange.eq(i9)) return false;
    let n22 = be7(this.dom, i9);
    return n22 && !this.selectionChanged && t5.inputState.lastFocusTime > Date.now() - 200 && t5.inputState.lastTouchTime < Date.now() - 300 && bo2(this.dom, i9) ? (this.view.inputState.lastFocusTime = 0, t5.docView.updateSelection(), false) : (this.selectionRange.setRange(i9), n22 && (this.selectionChanged = true), true);
  }
  setSelectionRange(t5, e4) {
    this.selectionRange.set(t5.node, t5.offset, e4.node, e4.offset), this.selectionChanged = false;
  }
  clearSelectionRange() {
    this.selectionRange.set(null, 0, null, 0);
  }
  listenForScroll() {
    this.parentCheck = -1;
    let t5 = 0, e4 = null;
    for (let i9 = this.dom; i9; ) if (i9.nodeType == 1) !e4 && t5 < this.scrollTargets.length && this.scrollTargets[t5] == i9 ? t5++ : e4 || (e4 = this.scrollTargets.slice(0, t5)), e4 && e4.push(i9), i9 = i9.assignedSlot || i9.parentNode;
    else if (i9.nodeType == 11) i9 = i9.host;
    else break;
    if (t5 < this.scrollTargets.length && !e4 && (e4 = this.scrollTargets.slice(0, t5)), e4) {
      for (let i9 of this.scrollTargets) i9.removeEventListener("scroll", this.onScroll);
      for (let i9 of this.scrollTargets = e4) i9.addEventListener("scroll", this.onScroll);
    }
  }
  ignore(t5) {
    if (!this.active) return t5();
    try {
      return this.stop(), t5();
    } finally {
      this.start(), this.clear();
    }
  }
  start() {
    this.active || (this.observer.observe(this.dom, wr2), Ue6 && this.dom.addEventListener("DOMCharacterDataModified", this.onCharData), this.active = true);
  }
  stop() {
    this.active && (this.active = false, this.observer.disconnect(), Ue6 && this.dom.removeEventListener("DOMCharacterDataModified", this.onCharData));
  }
  clear() {
    this.processRecords(), this.queue.length = 0, this.selectionChanged = false;
  }
  delayAndroidKey(t5, e4) {
    var i9;
    if (!this.delayedAndroidKey) {
      let n22 = () => {
        let o4 = this.delayedAndroidKey;
        o4 && (this.clearDelayedAndroidKey(), this.view.inputState.lastKeyCode = o4.keyCode, this.view.inputState.lastKeyTime = Date.now(), !this.flush() && o4.force && Dt5(this.dom, o4.key, o4.keyCode));
      };
      this.flushingAndroidKey = this.view.win.requestAnimationFrame(n22);
    }
    (!this.delayedAndroidKey || t5 == "Enter") && (this.delayedAndroidKey = {
      key: t5,
      keyCode: e4,
      force: this.lastChange < Date.now() - 50 || !!(!((i9 = this.delayedAndroidKey) === null || i9 === void 0) && i9.force)
    });
  }
  clearDelayedAndroidKey() {
    this.win.cancelAnimationFrame(this.flushingAndroidKey), this.delayedAndroidKey = null, this.flushingAndroidKey = -1;
  }
  flushSoon() {
    this.delayedFlush < 0 && (this.delayedFlush = this.view.win.requestAnimationFrame(() => {
      this.delayedFlush = -1, this.flush();
    }));
  }
  forceFlush() {
    this.delayedFlush >= 0 && (this.view.win.cancelAnimationFrame(this.delayedFlush), this.delayedFlush = -1), this.flush();
  }
  pendingRecords() {
    for (let t5 of this.observer.takeRecords()) this.queue.push(t5);
    return this.queue;
  }
  processRecords() {
    let t5 = this.pendingRecords();
    t5.length && (this.queue = []);
    let e4 = -1, i9 = -1, n22 = false;
    for (let o4 of t5) {
      let r2 = this.readMutation(o4);
      r2 && (r2.typeOver && (n22 = true), e4 == -1 ? { from: e4, to: i9 } = r2 : (e4 = Math.min(r2.from, e4), i9 = Math.max(r2.to, i9)));
    }
    return {
      from: e4,
      to: i9,
      typeOver: n22
    };
  }
  readChange() {
    let { from: t5, to: e4, typeOver: i9 } = this.processRecords(), n22 = this.selectionChanged && be7(this.dom, this.selectionRange);
    if (t5 < 0 && !n22) return null;
    t5 > -1 && (this.lastChange = Date.now()), this.view.inputState.lastFocusTime = 0, this.selectionChanged = false;
    let o4 = new vi(this.view, t5, e4, i9);
    return this.view.docView.domChanged = {
      newSel: o4.newSel ? o4.newSel.main : null
    }, o4;
  }
  flush(t5 = true) {
    if (this.delayedFlush >= 0 || this.delayedAndroidKey) return false;
    t5 && this.readSelectionRange();
    let e4 = this.readChange();
    if (!e4) return this.view.requestMeasure(), false;
    let i9 = this.view.state, n22 = On2(this.view, e4);
    return this.view.state == i9 && (e4.domChanged || e4.newSel && !e4.newSel.main.eq(this.view.state.selection.main)) && this.view.update([]), n22;
  }
  readMutation(t5) {
    let e4 = this.view.docView.tile.nearest(t5.target);
    if (!e4 || e4.isWidget()) return null;
    if (e4.markDirty(t5.type == "attributes"), t5.type == "childList") {
      let i9 = Ls2(e4, t5.previousSibling || t5.target.previousSibling, -1), n22 = Ls2(e4, t5.nextSibling || t5.target.nextSibling, 1);
      return {
        from: i9 ? e4.posAfter(i9) : e4.posAtStart,
        to: n22 ? e4.posBefore(n22) : e4.posAtEnd,
        typeOver: false
      };
    } else return t5.type == "characterData" ? {
      from: e4.posAtStart,
      to: e4.posAtEnd,
      typeOver: t5.target.nodeValue == t5.oldValue
    } : null;
  }
  setWindow(t5) {
    t5 != this.win && (this.removeWindowListeners(this.win), this.win = t5, this.addWindowListeners(this.win));
  }
  addWindowListeners(t5) {
    t5.addEventListener("resize", this.onResize), this.printQuery ? this.printQuery.addEventListener ? this.printQuery.addEventListener("change", this.onPrint) : this.printQuery.addListener(this.onPrint) : t5.addEventListener("beforeprint", this.onPrint), t5.addEventListener("scroll", this.onScroll), t5.document.addEventListener("selectionchange", this.onSelectionChange);
  }
  removeWindowListeners(t5) {
    t5.removeEventListener("scroll", this.onScroll), t5.removeEventListener("resize", this.onResize), this.printQuery ? this.printQuery.removeEventListener ? this.printQuery.removeEventListener("change", this.onPrint) : this.printQuery.removeListener(this.onPrint) : t5.removeEventListener("beforeprint", this.onPrint), t5.document.removeEventListener("selectionchange", this.onSelectionChange);
  }
  update(t5) {
    this.editContext && (this.editContext.update(t5), t5.startState.facet(tt6) != t5.state.facet(tt6) && (t5.view.contentDOM.editContext = t5.state.facet(tt6) ? this.editContext.editContext : null));
  }
  destroy() {
    var t5, e4, i9;
    this.stop(), (t5 = this.intersection) === null || t5 === void 0 || t5.disconnect(), (e4 = this.gapIntersection) === null || e4 === void 0 || e4.disconnect(), (i9 = this.resizeScroll) === null || i9 === void 0 || i9.disconnect();
    for (let n22 of this.scrollTargets) n22.removeEventListener("scroll", this.onScroll);
    this.removeWindowListeners(this.win), clearTimeout(this.parentCheck), clearTimeout(this.resizeTimeout), this.win.cancelAnimationFrame(this.delayedFlush), this.win.cancelAnimationFrame(this.flushingAndroidKey), this.editContext && (this.view.contentDOM.editContext = null, this.editContext.destroy());
  }
};
function Ls2(s99, t5, e4) {
  for (; t5; ) {
    let i9 = B9.get(t5);
    if (i9 && i9.parent == s99) return i9;
    let n22 = t5.parentNode;
    t5 = n22 != s99.dom ? n22 : e4 > 0 ? t5.nextSibling : t5.previousSibling;
  }
  return null;
}
function Rs2(s99, t5) {
  let e4 = t5.startContainer, i9 = t5.startOffset, n22 = t5.endContainer, o4 = t5.endOffset, r2 = s99.docView.domAtPos(s99.state.selection.main.anchor, 1);
  return qt3(r2.node, r2.offset, n22, o4) && ([e4, i9, n22, o4] = [
    n22,
    o4,
    e4,
    i9
  ]), {
    anchorNode: e4,
    anchorOffset: i9,
    focusNode: n22,
    focusOffset: o4
  };
}
function xr2(s99, t5) {
  if (t5.getComposedRanges) {
    let n22 = t5.getComposedRanges(s99.root)[0];
    if (n22) return Rs2(s99, n22);
  }
  let e4 = null;
  function i9(n22) {
    n22.preventDefault(), n22.stopImmediatePropagation(), e4 = n22.getTargetRanges()[0];
  }
  return s99.contentDOM.addEventListener("beforeinput", i9, true), s99.dom.ownerDocument.execCommand("indent"), s99.contentDOM.removeEventListener("beforeinput", i9, true), e4 ? Rs2(s99, e4) : null;
}
var Pi2 = class {
  constructor(t5) {
    this.from = 0, this.to = 0, this.pendingContextChange = null, this.handlers = /* @__PURE__ */ Object.create(null), this.composing = null, this.resetRange(t5.state);
    let e4 = this.editContext = new globalThis.EditContext({
      text: t5.state.doc.sliceString(this.from, this.to),
      selectionStart: this.toContextPos(Math.max(this.from, Math.min(this.to, t5.state.selection.main.anchor))),
      selectionEnd: this.toContextPos(t5.state.selection.main.head)
    });
    this.handlers.textupdate = (i9) => {
      let n22 = t5.state.selection.main, { anchor: o4, head: r2 } = n22, l11 = this.toEditorPos(i9.updateRangeStart), a2 = this.toEditorPos(i9.updateRangeEnd);
      t5.inputState.composing >= 0 && !this.composing && (this.composing = {
        contextBase: i9.updateRangeStart,
        editorBase: l11,
        drifted: false
      });
      let h3 = a2 - l11 > i9.text.length;
      l11 == this.from && o4 < this.from ? l11 = o4 : a2 == this.to && o4 > this.to && (a2 = o4);
      let c4 = Ln2(t5.state.sliceDoc(l11, a2), i9.text, (h3 ? n22.from : n22.to) - l11, h3 ? "end" : null);
      if (!c4) {
        let d5 = x8.single(this.toEditorPos(i9.selectionStart), this.toEditorPos(i9.selectionEnd));
        d5.main.eq(n22) || t5.dispatch({
          selection: d5,
          userEvent: "select"
        });
        return;
      }
      let f2 = {
        from: c4.from + l11,
        to: c4.toA + l11,
        insert: m7.of(i9.text.slice(c4.from, c4.toB).split(`
`))
      };
      if ((y8.mac || y8.android) && f2.from == r2 - 1 && /^\. ?$/.test(i9.text) && t5.contentDOM.getAttribute("autocorrect") == "off" && (f2 = {
        from: l11,
        to: a2,
        insert: m7.of([
          i9.text.replace(".", " ")
        ])
      }), this.pendingContextChange = f2, !t5.state.readOnly) {
        let d5 = this.to - this.from + (f2.to - f2.from + f2.insert.length);
        rs2(t5, f2, x8.single(this.toEditorPos(i9.selectionStart, d5), this.toEditorPos(i9.selectionEnd, d5)));
      }
      this.pendingContextChange && (this.revertPending(t5.state), this.setSelection(t5.state)), f2.from < f2.to && !f2.insert.length && t5.inputState.composing >= 0 && !/[\\p{Alphabetic}\\p{Number}_]/.test(e4.text.slice(Math.max(0, i9.updateRangeStart - 1), Math.min(e4.text.length, i9.updateRangeStart + 1))) && this.handlers.compositionend(i9);
    }, this.handlers.characterboundsupdate = (i9) => {
      let n22 = [], o4 = null;
      for (let r2 = this.toEditorPos(i9.rangeStart), l11 = this.toEditorPos(i9.rangeEnd); r2 < l11; r2++) {
        let a2 = t5.coordsForChar(r2);
        o4 = a2 && new DOMRect(a2.left, a2.top, a2.right - a2.left, a2.bottom - a2.top) || o4 || new DOMRect(), n22.push(o4);
      }
      e4.updateCharacterBounds(i9.rangeStart, n22);
    }, this.handlers.textformatupdate = (i9) => {
      let n22 = [];
      for (let o4 of i9.getTextFormats()) {
        let r2 = o4.underlineStyle, l11 = o4.underlineThickness;
        if (!/none/i.test(r2) && !/none/i.test(l11)) {
          let a2 = this.toEditorPos(o4.rangeStart), h3 = this.toEditorPos(o4.rangeEnd);
          if (a2 < h3) {
            let c4 = `text-decoration: underline ${/^[a-z]/.test(r2) ? r2 + " " : r2 == "Dashed" ? "dashed " : r2 == "Squiggle" ? "wavy " : ""}${/thin/i.test(l11) ? 1 : 2}px`;
            n22.push(T8.mark({
              attributes: {
                style: c4
              }
            }).range(a2, h3));
          }
        }
      }
      t5.dispatch({
        effects: wn2.of(T8.set(n22))
      });
    }, this.handlers.compositionstart = () => {
      t5.inputState.composing < 0 && (t5.inputState.composing = 0, t5.inputState.compositionFirstChange = true);
    }, this.handlers.compositionend = () => {
      if (t5.inputState.composing = -1, t5.inputState.compositionFirstChange = null, this.composing) {
        let { drifted: i9 } = this.composing;
        this.composing = null, i9 && this.reset(t5.state);
      }
    };
    for (let i9 in this.handlers) e4.addEventListener(i9, this.handlers[i9]);
    this.measureReq = {
      read: (i9) => {
        this.editContext.updateControlBounds(i9.contentDOM.getBoundingClientRect());
        let n22 = Jt3(i9.root);
        n22 && n22.rangeCount && this.editContext.updateSelectionBounds(n22.getRangeAt(0).getBoundingClientRect());
      }
    };
  }
  applyEdits(t5) {
    let e4 = 0, i9 = false, n22 = this.pendingContextChange;
    return t5.changes.iterChanges((o4, r2, l11, a2, h3) => {
      if (i9) return;
      let c4 = h3.length - (r2 - o4);
      if (n22 && r2 >= n22.to) if (n22.from == o4 && n22.to == r2 && n22.insert.eq(h3)) {
        n22 = this.pendingContextChange = null, e4 += c4, this.to += c4;
        return;
      } else n22 = null, this.revertPending(t5.state);
      if (o4 += e4, r2 += e4, r2 <= this.from) this.from += c4, this.to += c4;
      else if (o4 < this.to) {
        if (o4 < this.from || r2 > this.to || this.to - this.from + h3.length > 3e4) {
          i9 = true;
          return;
        }
        this.editContext.updateText(this.toContextPos(o4), this.toContextPos(r2), h3.toString()), this.to += c4;
      }
      e4 += c4;
    }), n22 && !i9 && this.revertPending(t5.state), !i9;
  }
  update(t5) {
    let e4 = this.pendingContextChange, i9 = t5.startState.selection.main;
    this.composing && (this.composing.drifted || !t5.changes.touchesRange(i9.from, i9.to) && t5.transactions.some((n22) => !n22.isUserEvent("input.type") && n22.changes.touchesRange(this.from, this.to))) ? (this.composing.drifted = true, this.composing.editorBase = t5.changes.mapPos(this.composing.editorBase)) : !this.applyEdits(t5) || !this.rangeIsValid(t5.state) ? (this.pendingContextChange = null, this.reset(t5.state)) : (t5.docChanged || t5.selectionSet || e4) && this.setSelection(t5.state), (t5.geometryChanged || t5.docChanged || t5.selectionSet) && t5.view.requestMeasure(this.measureReq);
  }
  resetRange(t5) {
    let { head: e4 } = t5.selection.main;
    this.from = Math.max(0, e4 - 1e4), this.to = Math.min(t5.doc.length, e4 + 1e4);
  }
  reset(t5) {
    this.resetRange(t5), this.editContext.updateText(0, this.editContext.text.length, t5.doc.sliceString(this.from, this.to)), this.setSelection(t5);
  }
  revertPending(t5) {
    let e4 = this.pendingContextChange;
    this.pendingContextChange = null, this.editContext.updateText(this.toContextPos(e4.from), this.toContextPos(e4.from + e4.insert.length), t5.doc.sliceString(e4.from, e4.to));
  }
  setSelection(t5) {
    let { main: e4 } = t5.selection, i9 = this.toContextPos(Math.max(this.from, Math.min(this.to, e4.anchor))), n22 = this.toContextPos(e4.head);
    (this.editContext.selectionStart != i9 || this.editContext.selectionEnd != n22) && this.editContext.updateSelection(i9, n22);
  }
  rangeIsValid(t5) {
    let { head: e4 } = t5.selection.main;
    return !(this.from > 0 && e4 - this.from < 500 || this.to < t5.doc.length && this.to - e4 < 500 || this.to - this.from > 1e4 * 3);
  }
  toEditorPos(t5, e4 = this.to - this.from) {
    t5 = Math.min(t5, e4);
    let i9 = this.composing;
    return i9 && i9.drifted ? i9.editorBase + (t5 - i9.contextBase) : t5 + this.from;
  }
  toContextPos(t5) {
    let e4 = this.composing;
    return e4 && e4.drifted ? e4.contextBase + (t5 - e4.editorBase) : t5 - this.from;
  }
  destroy() {
    for (let t5 in this.handlers) this.editContext.removeEventListener(t5, this.handlers[t5]);
  }
};
var k8 = class s85 {
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
    return !!this.inputState && this.inputState.composing > 0;
  }
  get compositionStarted() {
    return !!this.inputState && this.inputState.composing >= 0;
  }
  get root() {
    return this._root;
  }
  get win() {
    return this.dom.ownerDocument.defaultView || globalThis;
  }
  constructor(t5 = {}) {
    var e4;
    this.plugins = [], this.pluginMap = /* @__PURE__ */ new Map(), this.editorAttrs = {}, this.contentAttrs = {}, this.bidiCache = [], this.destroyed = false, this.updateState = 2, this.measureScheduled = -1, this.measureRequests = [], this.contentDOM = document.createElement("div"), this.scrollDOM = document.createElement("div"), this.scrollDOM.tabIndex = -1, this.scrollDOM.className = "cm-scroller", this.scrollDOM.appendChild(this.contentDOM), this.announceDOM = document.createElement("div"), this.announceDOM.className = "cm-announced", this.announceDOM.setAttribute("aria-live", "polite"), this.dom = document.createElement("div"), this.dom.appendChild(this.announceDOM), this.dom.appendChild(this.scrollDOM), t5.parent && t5.parent.appendChild(this.dom);
    let { dispatch: i9 } = t5;
    this.dispatchTransactions = t5.dispatchTransactions || i9 && ((n22) => n22.forEach((o4) => i9(o4, this))) || ((n22) => this.update(n22)), this.dispatch = this.dispatch.bind(this), this._root = t5.root || mo2(t5.parent) || document, this.viewState = new Pe8(t5.state || P7.create(t5)), t5.scrollTo && t5.scrollTo.is(ae9) && (this.viewState.scrollTarget = t5.scrollTo.value.clip(this.viewState.state)), this.plugins = this.state.facet(St4).map((n22) => new _t3(n22));
    for (let n22 of this.plugins) n22.update(this);
    this.observer = new Hi2(this), this.inputState = new Si2(this), this.inputState.ensureHandlers(this.plugins), this.docView = new Oe6(this), this.mountStyles(), this.updateAttrs(), this.updateState = 0, this.requestMeasure(), !((e4 = document.fonts) === null || e4 === void 0) && e4.ready && document.fonts.ready.then(() => {
      this.viewState.mustMeasureContent = true, this.requestMeasure();
    });
  }
  dispatch(...t5) {
    let e4 = t5.length == 1 && t5[0] instanceof S7 ? t5 : t5.length == 1 && Array.isArray(t5[0]) ? t5[0] : [
      this.state.update(...t5)
    ];
    this.dispatchTransactions(e4, this);
  }
  update(t5) {
    if (this.updateState != 0) throw new Error("Calls to EditorView.update are not allowed while an update is in progress");
    let e4 = false, i9 = false, n22, o4 = this.state;
    for (let d5 of t5) {
      if (d5.startState != o4) throw new RangeError("Trying to update state with a transaction that doesn't start from the previous state.");
      o4 = d5.state;
    }
    if (this.destroyed) {
      this.viewState.state = o4;
      return;
    }
    let r2 = this.hasFocus, l11 = 0, a2 = null;
    t5.some((d5) => d5.annotation(Nn2)) ? (this.inputState.notifiedFocused = r2, l11 = 1) : r2 != this.inputState.notifiedFocused && (this.inputState.notifiedFocused = r2, a2 = Wn2(o4, r2), a2 || (l11 = 1));
    let h3 = this.observer.delayedAndroidKey, c4 = null;
    if (h3 ? (this.observer.clearDelayedAndroidKey(), c4 = this.observer.readChange(), (c4 && !this.state.doc.eq(o4.doc) || !this.state.selection.eq(o4.selection)) && (c4 = null)) : this.observer.clear(), o4.facet(P7.phrases) != this.state.facet(P7.phrases)) return this.setState(o4);
    n22 = Te8.create(this, o4, t5), n22.flags |= l11;
    let f2 = this.viewState.scrollTarget;
    try {
      this.updateState = 2;
      for (let d5 of t5) {
        if (f2 && (f2 = f2.map(d5.changes)), d5.scrollIntoView) {
          let { main: u5 } = d5.state.selection;
          f2 = new Kt3(u5.empty ? u5 : x8.cursor(u5.head, u5.head > u5.anchor ? -1 : 1));
        }
        for (let u5 of d5.effects) u5.is(ae9) && (f2 = u5.value.clip(this.state));
      }
      this.viewState.update(n22, f2), this.bidiCache = Ne5.update(this.bidiCache, n22.changes), n22.empty || (this.updatePlugins(n22), this.inputState.update(n22)), e4 = this.docView.update(n22), this.state.facet(Nt4) != this.styleModules && this.mountStyles(), i9 = this.updateAttrs(), this.showAnnouncements(t5), this.docView.updateSelection(e4, t5.some((d5) => d5.isUserEvent("select.pointer")));
    } finally {
      this.updateState = 0;
    }
    if (n22.startState.facet(ue8) != n22.state.facet(ue8) && (this.viewState.mustMeasureContent = true), (e4 || i9 || f2 || this.viewState.mustEnforceCursorAssoc || this.viewState.mustMeasureContent) && this.requestMeasure(), e4 && this.docViewUpdate(), !n22.empty) for (let d5 of this.state.facet(hi2)) try {
      d5(n22);
    } catch (u5) {
      U9(this.state, u5, "update listener");
    }
    (a2 || c4) && Promise.resolve().then(() => {
      a2 && this.state == a2.startState && this.dispatch(a2), c4 && !On2(this, c4) && h3.force && Dt5(this.contentDOM, h3.key, h3.keyCode);
    });
  }
  setState(t5) {
    if (this.updateState != 0) throw new Error("Calls to EditorView.setState are not allowed while an update is in progress");
    if (this.destroyed) {
      this.viewState.state = t5;
      return;
    }
    this.updateState = 2;
    let e4 = this.hasFocus;
    try {
      for (let i9 of this.plugins) i9.destroy(this);
      this.viewState = new Pe8(t5), this.plugins = t5.facet(St4).map((i9) => new _t3(i9)), this.pluginMap.clear();
      for (let i9 of this.plugins) i9.update(this);
      this.docView.destroy(), this.docView = new Oe6(this), this.inputState.ensureHandlers(this.plugins), this.mountStyles(), this.updateAttrs(), this.bidiCache = [];
    } finally {
      this.updateState = 0;
    }
    e4 && this.focus(), this.requestMeasure();
  }
  updatePlugins(t5) {
    let e4 = t5.startState.facet(St4), i9 = t5.state.facet(St4);
    if (e4 != i9) {
      let n22 = [];
      for (let o4 of i9) {
        let r2 = e4.indexOf(o4);
        if (r2 < 0) n22.push(new _t3(o4));
        else {
          let l11 = this.plugins[r2];
          l11.mustUpdate = t5, n22.push(l11);
        }
      }
      for (let o4 of this.plugins) o4.mustUpdate != t5 && o4.destroy(this);
      this.plugins = n22, this.pluginMap.clear();
    } else for (let n22 of this.plugins) n22.mustUpdate = t5;
    for (let n22 = 0; n22 < this.plugins.length; n22++) this.plugins[n22].update(this);
    e4 != i9 && this.inputState.ensureHandlers(this.plugins);
  }
  docViewUpdate() {
    for (let t5 of this.plugins) {
      let e4 = t5.value;
      if (e4 && e4.docViewUpdate) try {
        e4.docViewUpdate(this);
      } catch (i9) {
        U9(this.state, i9, "doc view update listener");
      }
    }
  }
  measure(t5 = true) {
    if (this.destroyed) return;
    if (this.measureScheduled > -1 && this.win.cancelAnimationFrame(this.measureScheduled), this.observer.delayedAndroidKey) {
      this.measureScheduled = -1, this.requestMeasure();
      return;
    }
    this.measureScheduled = 0, t5 && this.observer.forceFlush();
    let e4 = null, i9 = this.scrollDOM, n22 = i9.scrollTop * this.scaleY, { scrollAnchorPos: o4, scrollAnchorHeight: r2 } = this.viewState;
    Math.abs(n22 - this.viewState.scrollTop) > 1 && (r2 = -1), this.viewState.scrollAnchorHeight = -1;
    try {
      for (let l11 = 0; ; l11++) {
        if (r2 < 0) if (Zs2(i9)) o4 = -1, r2 = this.viewState.heightMap.height;
        else {
          let u5 = this.viewState.scrollAnchorAt(n22);
          o4 = u5.from, r2 = u5.top;
        }
        this.updateState = 1;
        let a2 = this.viewState.measure(this);
        if (!a2 && !this.measureRequests.length && this.viewState.scrollTarget == null) break;
        if (l11 > 5) {
          console.warn(this.measureRequests.length ? "Measure loop restarted more than 5 times" : "Viewport failed to stabilize");
          break;
        }
        let h3 = [];
        a2 & 4 || ([this.measureRequests, h3] = [
          h3,
          this.measureRequests
        ]);
        let c4 = h3.map((u5) => {
          try {
            return u5.read(this);
          } catch (p5) {
            return U9(this.state, p5), Bs2;
          }
        }), f2 = Te8.create(this, this.state, []), d5 = false;
        f2.flags |= a2, e4 ? e4.flags |= a2 : e4 = f2, this.updateState = 2, f2.empty || (this.updatePlugins(f2), this.inputState.update(f2), this.updateAttrs(), d5 = this.docView.update(f2), d5 && this.docViewUpdate());
        for (let u5 = 0; u5 < h3.length; u5++) if (c4[u5] != Bs2) try {
          let p5 = h3[u5];
          p5.write && p5.write(c4[u5], this);
        } catch (p5) {
          U9(this.state, p5);
        }
        if (d5 && this.docView.updateSelection(true), !f2.viewportChanged && this.measureRequests.length == 0) {
          if (this.viewState.editorHeight) if (this.viewState.scrollTarget) {
            this.docView.scrollIntoView(this.viewState.scrollTarget), this.viewState.scrollTarget = null, r2 = -1;
            continue;
          } else {
            let p5 = (o4 < 0 ? this.viewState.heightMap.height : this.viewState.lineBlockAt(o4).top) - r2;
            if (p5 > 1 || p5 < -1) {
              n22 = n22 + p5, i9.scrollTop = n22 / this.scaleY, r2 = -1;
              continue;
            }
          }
          break;
        }
      }
    } finally {
      this.updateState = 0, this.measureScheduled = -1;
    }
    if (e4 && !e4.empty) for (let l11 of this.state.facet(hi2)) l11(e4);
  }
  get themeClasses() {
    return Bi2 + " " + (this.state.facet(Ri2) ? In2 : Fn2) + " " + this.state.facet(ue8);
  }
  updateAttrs() {
    let t5 = Es2(this, xn2, {
      class: "cm-editor" + (this.hasFocus ? " cm-focused " : " ") + this.themeClasses
    }), e4 = {
      spellcheck: "false",
      autocorrect: "off",
      autocapitalize: "off",
      writingsuggestions: "false",
      translate: "no",
      contenteditable: this.state.facet(tt6) ? "true" : "false",
      class: "cm-content",
      style: `${y8.tabSize}: ${this.state.tabSize}`,
      role: "textbox",
      "aria-multiline": "true"
    };
    this.state.readOnly && (e4["aria-readonly"] = "true"), Es2(this, qe6, e4);
    let i9 = this.observer.ignore(() => {
      let n22 = fs(this.contentDOM, this.contentAttrs, e4), o4 = fs(this.dom, this.editorAttrs, t5);
      return n22 || o4;
    });
    return this.editorAttrs = t5, this.contentAttrs = e4, i9;
  }
  showAnnouncements(t5) {
    let e4 = true;
    for (let i9 of t5) for (let n22 of i9.effects) if (n22.is(s85.announce)) {
      e4 && (this.announceDOM.textContent = ""), e4 = false;
      let o4 = this.announceDOM.appendChild(document.createElement("div"));
      o4.textContent = n22.value;
    }
  }
  mountStyles() {
    this.styleModules = this.state.facet(Nt4);
    let t5 = this.state.facet(s85.cspNonce);
    T2.mount(this.root, this.styleModules.concat(yr2).reverse(), t5 ? {
      nonce: t5
    } : void 0);
  }
  readMeasured() {
    if (this.updateState == 2) throw new Error("Reading the editor layout isn't allowed during an update");
    this.updateState == 0 && this.measureScheduled > -1 && this.measure(false);
  }
  requestMeasure(t5) {
    if (this.measureScheduled < 0 && (this.measureScheduled = this.win.requestAnimationFrame(() => this.measure())), t5) {
      if (this.measureRequests.indexOf(t5) > -1) return;
      if (t5.key != null) {
        for (let e4 = 0; e4 < this.measureRequests.length; e4++) if (this.measureRequests[e4].key === t5.key) {
          this.measureRequests[e4] = t5;
          return;
        }
      }
      this.measureRequests.push(t5);
    }
  }
  plugin(t5) {
    let e4 = this.pluginMap.get(t5);
    return (e4 === void 0 || e4 && e4.plugin != t5) && this.pluginMap.set(t5, e4 = this.plugins.find((i9) => i9.plugin == t5) || null), e4 && e4.update(this).value;
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
  get scaleX() {
    return this.viewState.scaleX;
  }
  get scaleY() {
    return this.viewState.scaleY;
  }
  elementAtHeight(t5) {
    return this.readMeasured(), this.viewState.elementAtHeight(t5);
  }
  lineBlockAtHeight(t5) {
    return this.readMeasured(), this.viewState.lineBlockAtHeight(t5);
  }
  get viewportLineBlocks() {
    return this.viewState.viewportLines;
  }
  lineBlockAt(t5) {
    return this.viewState.lineBlockAt(t5);
  }
  get contentHeight() {
    return this.viewState.contentHeight;
  }
  moveByChar(t5, e4, i9) {
    return Ge5(this, t5, bs2(this, t5, e4, i9));
  }
  moveByGroup(t5, e4) {
    return Ge5(this, t5, bs2(this, t5, e4, (i9) => Ko(this, t5.head, i9)));
  }
  visualLineSide(t5, e4) {
    let i9 = this.bidiSpans(t5), n22 = this.textDirectionAt(t5.from), o4 = i9[e4 ? i9.length - 1 : 0];
    return x8.cursor(o4.side(e4, n22) + t5.from, o4.forward(!e4, n22) ? 1 : -1);
  }
  moveToLineBoundary(t5, e4, i9 = true) {
    return qo(this, t5, e4, i9);
  }
  moveVertically(t5, e4, i9) {
    return Ge5(this, t5, _o(this, t5, e4, i9));
  }
  domAtPos(t5, e4 = 1) {
    return this.docView.domAtPos(t5, e4);
  }
  posAtDOM(t5, e4 = 0) {
    return this.docView.posFromDOM(t5, e4);
  }
  posAtCoords(t5, e4 = true) {
    this.readMeasured();
    let i9 = wi2(this, t5, e4);
    return i9 && i9.pos;
  }
  posAndSideAtCoords(t5, e4 = true) {
    return this.readMeasured(), wi2(this, t5, e4);
  }
  coordsAtPos(t5, e4 = 1) {
    this.readMeasured();
    let i9 = this.docView.coordsAt(t5, e4);
    if (!i9 || i9.left == i9.right) return i9;
    let n22 = this.state.doc.lineAt(t5), o4 = this.bidiSpans(n22), r2 = o4[j8.find(o4, t5 - n22.from, -1, e4)];
    return Zt3(i9, r2.dir == R9.LTR == e4 > 0);
  }
  coordsForChar(t5) {
    return this.readMeasured(), this.docView.coordsForChar(t5);
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
  textDirectionAt(t5) {
    return !this.state.facet(mn) || t5 < this.viewport.from || t5 > this.viewport.to ? this.textDirection : (this.readMeasured(), this.docView.textDirectionAt(t5));
  }
  get lineWrapping() {
    return this.viewState.heightOracle.lineWrapping;
  }
  bidiSpans(t5) {
    if (t5.length > vr2) return ln3(t5.length);
    let e4 = this.textDirectionAt(t5.from), i9;
    for (let o4 of this.bidiCache) if (o4.from == t5.from && o4.dir == e4 && (o4.fresh || on3(o4.isolates, i9 = ps2(this, t5)))) return o4.order;
    i9 || (i9 = ps2(this, t5));
    let n22 = rn3(t5.text, e4, i9);
    return this.bidiCache.push(new Ne5(t5.from, t5.to, e4, i9, true, n22)), n22;
  }
  get hasFocus() {
    var t5;
    return (this.dom.ownerDocument.hasFocus() || y8.safari && ((t5 = this.inputState) === null || t5 === void 0 ? void 0 : t5.lastContextMenu) > Date.now() - 3e4) && this.root.activeElement == this.contentDOM;
  }
  focus() {
    this.observer.ignore(() => {
      Js2(this.contentDOM), this.docView.updateSelection();
    });
  }
  setRoot(t5) {
    this._root != t5 && (this._root = t5, this.observer.setWindow((t5.nodeType == 9 ? t5 : t5.ownerDocument).defaultView || globalThis), this.mountStyles());
  }
  destroy() {
    this.root.activeElement == this.contentDOM && this.contentDOM.blur();
    for (let t5 of this.plugins) t5.destroy(this);
    this.plugins = [], this.inputState.destroy(), this.docView.destroy(), this.dom.remove(), this.observer.destroy(), this.measureScheduled > -1 && this.win.cancelAnimationFrame(this.measureScheduled), this.destroyed = true;
  }
  static scrollIntoView(t5, e4 = {}) {
    return ae9.of(new Kt3(typeof t5 == "number" ? x8.cursor(t5) : t5, e4.y, e4.x, e4.yMargin, e4.xMargin));
  }
  scrollSnapshot() {
    let { scrollTop: t5, scrollLeft: e4 } = this.scrollDOM, i9 = this.viewState.scrollAnchorAt(t5);
    return ae9.of(new Kt3(x8.cursor(i9.from), "start", "start", i9.top - t5, e4, true));
  }
  setTabFocusMode(t5) {
    t5 == null ? this.inputState.tabFocusMode = this.inputState.tabFocusMode < 0 ? 0 : -1 : typeof t5 == "boolean" ? this.inputState.tabFocusMode = t5 ? 0 : -1 : this.inputState.tabFocusMode != 0 && (this.inputState.tabFocusMode = Date.now() + t5);
  }
  static domEventHandlers(t5) {
    return N10.define(() => ({}), {
      eventHandlers: t5
    });
  }
  static domEventObservers(t5) {
    return N10.define(() => ({}), {
      eventObservers: t5
    });
  }
  static theme(t5, e4) {
    let i9 = T2.newName(), n22 = [
      ue8.of(i9),
      Nt4.of(Ei2(`.${i9}`, t5))
    ];
    return e4 && e4.dark && n22.push(Ri2.of(true)), n22;
  }
  static baseTheme(t5) {
    return st4.lowest(Nt4.of(Ei2("." + Bi2, t5, zn2)));
  }
  static findFromDOM(t5) {
    var e4;
    let i9 = t5.querySelector(".cm-content"), n22 = i9 && B9.get(i9) || B9.get(t5);
    return ((e4 = n22?.root) === null || e4 === void 0 ? void 0 : e4.view) || null;
  }
};
k8.styleModule = Nt4;
k8.inputHandler = pn;
k8.clipboardInputFilter = is2;
k8.clipboardOutputFilter = ss2;
k8.scrollHandler = yn2;
k8.focusChangeEffect = gn2;
k8.perLineTextDirection = mn;
k8.exceptionSink = un2;
k8.updateListener = hi2;
k8.editable = tt6;
k8.mouseSelectionStyle = dn2;
k8.dragMovesSelection = fn;
k8.clickAddsSelectionRange = cn2;
k8.decorations = Ke5;
k8.blockWrappers = vn2;
k8.outerDecorations = ns2;
k8.atomicRanges = ne8;
k8.bidiIsolatedRanges = Sn2;
k8.scrollMargins = Cn2;
k8.darkTheme = Ri2;
k8.cspNonce = k7.define({
  combine: (s99) => s99.length ? s99[0] : ""
});
k8.contentAttributes = qe6;
k8.editorAttributes = xn2;
k8.lineWrapping = k8.contentAttributes.of({
  class: "cm-lineWrapping"
});
k8.announce = v5.define();
var vr2 = 4096;
var Bs2 = {};
var Ne5 = class s86 {
  constructor(t5, e4, i9, n22, o4, r2) {
    this.from = t5, this.to = e4, this.dir = i9, this.isolates = n22, this.fresh = o4, this.order = r2;
  }
  static update(t5, e4) {
    if (e4.empty && !t5.some((o4) => o4.fresh)) return t5;
    let i9 = [], n22 = t5.length ? t5[t5.length - 1].dir : R9.LTR;
    for (let o4 = Math.max(0, t5.length - 10); o4 < t5.length; o4++) {
      let r2 = t5[o4];
      r2.dir == n22 && !e4.touchesRange(r2.from, r2.to) && i9.push(new s86(e4.mapPos(r2.from, 1), e4.mapPos(r2.to, -1), r2.dir, r2.isolates, false, r2.order));
    }
    return i9;
  }
};
function Es2(s99, t5, e4) {
  for (let i9 = s99.state.facet(t5), n22 = i9.length - 1; n22 >= 0; n22--) {
    let o4 = i9[n22], r2 = typeof o4 == "function" ? o4(s99) : o4;
    r2 && Zi2(r2, e4);
  }
  return e4;
}
var Sr2 = y8.mac ? "mac" : y8.windows ? "win" : y8.linux ? "linux" : "key";
function Cr2(s99, t5) {
  let e4 = s99.split(/-(?!$)/), i9 = e4[e4.length - 1];
  i9 == "Space" && (i9 = " ");
  let n22, o4, r2, l11;
  for (let a2 = 0; a2 < e4.length - 1; ++a2) {
    let h3 = e4[a2];
    if (/^(cmd|meta|m)$/i.test(h3)) l11 = true;
    else if (/^a(lt)?$/i.test(h3)) n22 = true;
    else if (/^(c|ctrl|control)$/i.test(h3)) o4 = true;
    else if (/^s(hift)?$/i.test(h3)) r2 = true;
    else if (/^mod$/i.test(h3)) t5 == "mac" ? l11 = true : o4 = true;
    else throw new Error("Unrecognized modifier name: " + h3);
  }
  return n22 && (i9 = "Alt-" + i9), o4 && (i9 = "Ctrl-" + i9), l11 && (i9 = "Meta-" + i9), r2 && (i9 = "Shift-" + i9), i9;
}
function pe7(s99, t5, e4) {
  return t5.altKey && (s99 = "Alt-" + s99), t5.ctrlKey && (s99 = "Ctrl-" + s99), t5.metaKey && (s99 = "Meta-" + s99), e4 !== false && t5.shiftKey && (s99 = "Shift-" + s99), s99;
}
var Mr2 = st4.default(k8.domEventHandlers({
  keydown(s99, t5) {
    return Kn2(qn2(t5.state), s99, t5, "editor");
  }
}));
var kr2 = k7.define({
  enables: Mr2
});
var Hs2 = /* @__PURE__ */ new WeakMap();
function qn2(s99) {
  let t5 = s99.facet(kr2), e4 = Hs2.get(t5);
  return e4 || Hs2.set(t5, e4 = Tr2(t5.reduce((i9, n22) => i9.concat(n22), []))), e4;
}
var rt5 = null;
var Ar2 = 4e3;
function Tr2(s99, t5 = Sr2) {
  let e4 = /* @__PURE__ */ Object.create(null), i9 = /* @__PURE__ */ Object.create(null), n22 = (r2, l11) => {
    let a2 = i9[r2];
    if (a2 == null) i9[r2] = l11;
    else if (a2 != l11) throw new Error("Key binding " + r2 + " is used both as a regular binding and as a multi-stroke prefix");
  }, o4 = (r2, l11, a2, h3, c4) => {
    var f2, d5;
    let u5 = e4[r2] || (e4[r2] = /* @__PURE__ */ Object.create(null)), p5 = l11.split(/ (?!$)/).map((b9) => Cr2(b9, t5));
    for (let b9 = 1; b9 < p5.length; b9++) {
      let w11 = p5.slice(0, b9).join(" ");
      n22(w11, true), u5[w11] || (u5[w11] = {
        preventDefault: true,
        stopPropagation: false,
        run: [
          (M14) => {
            let A11 = rt5 = {
              view: M14,
              prefix: w11,
              scope: r2
            };
            return setTimeout(() => {
              rt5 == A11 && (rt5 = null);
            }, Ar2), true;
          }
        ]
      });
    }
    let g6 = p5.join(" ");
    n22(g6, false);
    let m9 = u5[g6] || (u5[g6] = {
      preventDefault: false,
      stopPropagation: false,
      run: ((d5 = (f2 = u5._any) === null || f2 === void 0 ? void 0 : f2.run) === null || d5 === void 0 ? void 0 : d5.slice()) || []
    });
    a2 && m9.run.push(a2), h3 && (m9.preventDefault = true), c4 && (m9.stopPropagation = true);
  };
  for (let r2 of s99) {
    let l11 = r2.scope ? r2.scope.split(" ") : [
      "editor"
    ];
    if (r2.any) for (let h3 of l11) {
      let c4 = e4[h3] || (e4[h3] = /* @__PURE__ */ Object.create(null));
      c4._any || (c4._any = {
        preventDefault: false,
        stopPropagation: false,
        run: []
      });
      let { any: f2 } = r2;
      for (let d5 in c4) c4[d5].run.push((u5) => f2(u5, Ni2));
    }
    let a2 = r2[t5] || r2.key;
    if (a2) for (let h3 of l11) o4(h3, a2, r2.run, r2.preventDefault, r2.stopPropagation), r2.shift && o4(h3, "Shift-" + a2, r2.shift, r2.preventDefault, r2.stopPropagation);
  }
  return e4;
}
var Ni2 = null;
function Kn2(s99, t5, e4, i9) {
  Ni2 = t5;
  let n22 = g(t5), o4 = tt5(n22, 0), r2 = it5(o4) == n22.length && n22 != " ", l11 = "", a2 = false, h3 = false, c4 = false;
  rt5 && rt5.view == e4 && rt5.scope == i9 && (l11 = rt5.prefix + " ", Bn2.indexOf(t5.keyCode) < 0 && (h3 = true, rt5 = null));
  let f2 = /* @__PURE__ */ new Set(), d5 = (m9) => {
    if (m9) {
      for (let b9 of m9.run) if (!f2.has(b9) && (f2.add(b9), b9(e4))) return m9.stopPropagation && (c4 = true), true;
      m9.preventDefault && (m9.stopPropagation && (c4 = true), h3 = true);
    }
    return false;
  }, u5 = s99[i9], p5, g6;
  return u5 && (d5(u5[l11 + pe7(n22, t5, !r2)]) ? a2 = true : r2 && (t5.altKey || t5.metaKey || t5.ctrlKey) && !(y8.windows && t5.ctrlKey && t5.altKey) && !(y8.mac && t5.altKey && !(t5.ctrlKey || t5.metaKey)) && (p5 = t[t5.keyCode]) && p5 != n22 ? (d5(u5[l11 + pe7(p5, t5, true)]) || t5.shiftKey && (g6 = i[t5.keyCode]) != n22 && g6 != p5 && d5(u5[l11 + pe7(g6, t5, false)])) && (a2 = true) : r2 && t5.shiftKey && d5(u5[l11 + pe7(n22, t5, true)]) && (a2 = true), !a2 && d5(u5._any) && (a2 = true)), h3 && (a2 = true), a2 && c4 && t5.stopPropagation(), Ni2 = null, a2;
}
var ee7 = class s87 {
  constructor(t5, e4, i9, n22, o4) {
    this.className = t5, this.left = e4, this.top = i9, this.width = n22, this.height = o4;
  }
  draw() {
    let t5 = document.createElement("div");
    return t5.className = this.className, this.adjust(t5), t5;
  }
  update(t5, e4) {
    return e4.className != this.className ? false : (this.adjust(t5), true);
  }
  adjust(t5) {
    t5.style.left = this.left + "px", t5.style.top = this.top + "px", this.width != null && (t5.style.width = this.width + "px"), t5.style.height = this.height + "px";
  }
  eq(t5) {
    return this.left == t5.left && this.top == t5.top && this.width == t5.width && this.height == t5.height && this.className == t5.className;
  }
  static forRange(t5, e4, i9) {
    if (i9.empty) {
      let n22 = t5.coordsAtPos(i9.head, i9.assoc || 1);
      if (!n22) return [];
      let o4 = _n2(t5);
      return [
        new s87(e4, n22.left - o4.left, n22.top - o4.top, null, n22.bottom - n22.top)
      ];
    } else return Dr2(t5, e4, i9);
  }
};
function _n2(s99) {
  let t5 = s99.scrollDOM.getBoundingClientRect();
  return {
    left: (s99.textDirection == R9.LTR ? t5.left : t5.right - s99.scrollDOM.clientWidth * s99.scaleX) - s99.scrollDOM.scrollLeft * s99.scaleX,
    top: t5.top - s99.scrollDOM.scrollTop * s99.scaleY
  };
}
function Ps2(s99, t5, e4, i9) {
  let n22 = s99.coordsAtPos(t5, e4 * 2);
  if (!n22) return i9;
  let o4 = s99.dom.getBoundingClientRect(), r2 = (n22.top + n22.bottom) / 2, l11 = s99.posAtCoords({
    x: o4.left + 1,
    y: r2
  }), a2 = s99.posAtCoords({
    x: o4.right - 1,
    y: r2
  });
  return l11 == null || a2 == null ? i9 : {
    from: Math.max(i9.from, Math.min(l11, a2)),
    to: Math.min(i9.to, Math.max(l11, a2))
  };
}
function Dr2(s99, t5, e4) {
  if (e4.to <= s99.viewport.from || e4.from >= s99.viewport.to) return [];
  let i9 = Math.max(e4.from, s99.viewport.from), n22 = Math.min(e4.to, s99.viewport.to), o4 = s99.textDirection == R9.LTR, r2 = s99.contentDOM, l11 = r2.getBoundingClientRect(), a2 = _n2(s99), h3 = r2.querySelector(".cm-line"), c4 = h3 && globalThis.getComputedStyle(h3), f2 = l11.left + (c4 ? parseInt(c4.paddingLeft) + Math.min(0, parseInt(c4.textIndent)) : 0), d5 = l11.right - (c4 ? parseInt(c4.paddingRight) : 0), u5 = yi2(s99, i9, 1), p5 = yi2(s99, n22, -1), g6 = u5.type == P8.Text ? u5 : null, m9 = p5.type == P8.Text ? p5 : null;
  if (g6 && (s99.lineWrapping || u5.widgetLineBreaks) && (g6 = Ps2(s99, i9, 1, g6)), m9 && (s99.lineWrapping || p5.widgetLineBreaks) && (m9 = Ps2(s99, n22, -1, m9)), g6 && m9 && g6.from == m9.from && g6.to == m9.to) return w11(M14(e4.from, e4.to, g6));
  {
    let v8 = g6 ? M14(e4.from, null, g6) : A11(u5, false), x11 = m9 ? M14(null, e4.to, m9) : A11(p5, true), L10 = [];
    return (g6 || u5).to < (m9 || p5).from - (g6 && m9 ? 1 : 0) || u5.widgetLineBreaks > 1 && v8.bottom + s99.defaultLineHeight / 2 < x11.top ? L10.push(b9(f2, v8.bottom, d5, x11.top)) : v8.bottom < x11.top && s99.elementAtHeight((v8.bottom + x11.top) / 2).type == P8.Text && (v8.bottom = x11.top = (v8.bottom + x11.top) / 2), w11(v8).concat(L10).concat(w11(x11));
  }
  function b9(v8, x11, L10, H10) {
    return new ee7(t5, v8 - a2.left, x11 - a2.top, L10 - v8, H10 - x11);
  }
  function w11({ top: v8, bottom: x11, horizontal: L10 }) {
    let H10 = [];
    for (let nt7 = 0; nt7 < L10.length; nt7 += 2) H10.push(b9(L10[nt7], v8, L10[nt7 + 1], x11));
    return H10;
  }
  function M14(v8, x11, L10) {
    let H10 = 1e9, nt7 = -1e9, oe11 = [];
    function ls(dt6, ot9, xt7, ut5, Pt7) {
      let J8 = s99.coordsAtPos(dt6, dt6 == L10.to ? -2 : 2), Z14 = s99.coordsAtPos(xt7, xt7 == L10.from ? 2 : -2);
      !J8 || !Z14 || (H10 = Math.min(J8.top, Z14.top, H10), nt7 = Math.max(J8.bottom, Z14.bottom, nt7), Pt7 == R9.LTR ? oe11.push(o4 && ot9 ? f2 : J8.left, o4 && ut5 ? d5 : Z14.right) : oe11.push(!o4 && ut5 ? f2 : Z14.left, !o4 && ot9 ? d5 : J8.right));
    }
    let re10 = v8 ?? L10.from, le10 = x11 ?? L10.to;
    for (let dt6 of s99.visibleRanges) if (dt6.to > re10 && dt6.from < le10) for (let ot9 = Math.max(dt6.from, re10), xt7 = Math.min(dt6.to, le10); ; ) {
      let ut5 = s99.state.doc.lineAt(ot9);
      for (let Pt7 of s99.bidiSpans(ut5)) {
        let J8 = Pt7.from + ut5.from, Z14 = Pt7.to + ut5.from;
        if (J8 >= xt7) break;
        Z14 > ot9 && ls(Math.max(J8, ot9), v8 == null && J8 <= re10, Math.min(Z14, xt7), x11 == null && Z14 >= le10, Pt7.dir);
      }
      if (ot9 = ut5.to + 1, ot9 >= xt7) break;
    }
    return oe11.length == 0 && ls(re10, v8 == null, le10, x11 == null, s99.textDirection), {
      top: H10,
      bottom: nt7,
      horizontal: oe11
    };
  }
  function A11(v8, x11) {
    let L10 = l11.top + (x11 ? v8.top : v8.bottom);
    return {
      top: L10,
      bottom: L10,
      horizontal: []
    };
  }
}
function Or2(s99, t5) {
  return s99.constructor == t5.constructor && s99.eq(t5);
}
var Wi2 = class {
  constructor(t5, e4) {
    this.view = t5, this.layer = e4, this.drawn = [], this.scaleX = 1, this.scaleY = 1, this.measureReq = {
      read: this.measure.bind(this),
      write: this.draw.bind(this)
    }, this.dom = t5.scrollDOM.appendChild(document.createElement("div")), this.dom.classList.add("cm-layer"), e4.above && this.dom.classList.add("cm-layer-above"), e4.class && this.dom.classList.add(e4.class), this.scale(), this.dom.setAttribute("aria-hidden", "true"), this.setOrder(t5.state), t5.requestMeasure(this.measureReq), e4.mount && e4.mount(this.dom, t5);
  }
  update(t5) {
    t5.startState.facet(we6) != t5.state.facet(we6) && this.setOrder(t5.state), (this.layer.update(t5, this.dom) || t5.geometryChanged) && (this.scale(), t5.view.requestMeasure(this.measureReq));
  }
  docViewUpdate(t5) {
    this.layer.updateOnDocViewUpdate !== false && t5.requestMeasure(this.measureReq);
  }
  setOrder(t5) {
    let e4 = 0, i9 = t5.facet(we6);
    for (; e4 < i9.length && i9[e4] != this.layer; ) e4++;
    this.dom.style.zIndex = String((this.layer.above ? 150 : -1) - e4);
  }
  measure() {
    return this.layer.markers(this.view);
  }
  scale() {
    let { scaleX: t5, scaleY: e4 } = this.view;
    (t5 != this.scaleX || e4 != this.scaleY) && (this.scaleX = t5, this.scaleY = e4, this.dom.style.transform = `scale(${1 / t5}, ${1 / e4})`);
  }
  draw(t5) {
    if (t5.length != this.drawn.length || t5.some((e4, i9) => !Or2(e4, this.drawn[i9]))) {
      let e4 = this.dom.firstChild, i9 = 0;
      for (let n22 of t5) n22.update && e4 && n22.constructor && this.drawn[i9].constructor && n22.update(e4, this.drawn[i9]) ? (e4 = e4.nextSibling, i9++) : this.dom.insertBefore(n22.draw(), e4);
      for (; e4; ) {
        let n22 = e4.nextSibling;
        e4.remove(), e4 = n22;
      }
      this.drawn = t5, y8.safari && y8.safari_version >= 26 && (this.dom.style.display = this.dom.firstChild ? "" : "none");
    }
  }
  destroy() {
    this.layer.destroy && this.layer.destroy(this.dom, this.view), this.dom.remove();
  }
};
var we6 = k7.define();
function jn2(s99) {
  return [
    N10.define((t5) => new Wi2(t5, s99)),
    we6.of(s99)
  ];
}
var Ht4 = k7.define({
  combine(s99) {
    return rt4(s99, {
      cursorBlinkRate: 1200,
      drawRangeCursor: true
    }, {
      cursorBlinkRate: (t5, e4) => Math.min(t5, e4),
      drawRangeCursor: (t5, e4) => t5 || e4
    });
  }
});
function Yn2(s99) {
  return s99.startState.facet(Ht4) != s99.state.facet(Ht4);
}
var Lr2 = jn2({
  above: true,
  markers(s99) {
    let { state: t5 } = s99, e4 = t5.facet(Ht4), i9 = [];
    for (let n22 of t5.selection.ranges) {
      let o4 = n22 == t5.selection.main;
      if (n22.empty || e4.drawRangeCursor) {
        let r2 = o4 ? "cm-cursor cm-cursor-primary" : "cm-cursor cm-cursor-secondary", l11 = n22.empty ? n22 : x8.cursor(n22.head, n22.head > n22.anchor ? -1 : 1);
        for (let a2 of ee7.forRange(s99, r2, l11)) i9.push(a2);
      }
    }
    return i9;
  },
  update(s99, t5) {
    s99.transactions.some((i9) => i9.selection) && (t5.style.animationName = t5.style.animationName == "cm-blink" ? "cm-blink2" : "cm-blink");
    let e4 = Yn2(s99);
    return e4 && Ns2(s99.state, t5), s99.docChanged || s99.selectionSet || e4;
  },
  mount(s99, t5) {
    Ns2(t5.state, s99);
  },
  class: "cm-cursorLayer"
});
function Ns2(s99, t5) {
  t5.style.animationDuration = s99.facet(Ht4).cursorBlinkRate + "ms";
}
var Rr2 = jn2({
  above: false,
  markers(s99) {
    return s99.state.selection.ranges.map((t5) => t5.empty ? [] : ee7.forRange(s99, "cm-selectionBackground", t5)).reduce((t5, e4) => t5.concat(e4));
  },
  update(s99, t5) {
    return s99.docChanged || s99.selectionSet || s99.viewportChanged || Yn2(s99);
  },
  class: "cm-selectionLayer"
});
var Br2 = st4.highest(k8.theme({
  ".cm-line": {
    "& ::selection, &::selection": {
      backgroundColor: "transparent !important"
    },
    caretColor: "transparent !important"
  },
  ".cm-content": {
    caretColor: "transparent !important",
    "& :focus": {
      caretColor: "initial !important",
      "&::selection, & ::selection": {
        backgroundColor: "Highlight !important"
      }
    }
  }
}));
var Xn2 = v5.define({
  map(s99, t5) {
    return s99 == null ? null : t5.mapPos(s99);
  }
});
var Ft3 = z8.define({
  create() {
    return null;
  },
  update(s99, t5) {
    return s99 != null && (s99 = t5.changes.mapPos(s99)), t5.effects.reduce((e4, i9) => i9.is(Xn2) ? i9.value : e4, s99);
  }
});
var Er2 = N10.fromClass(class {
  constructor(s99) {
    this.view = s99, this.cursor = null, this.measureReq = {
      read: this.readPos.bind(this),
      write: this.drawCursor.bind(this)
    };
  }
  update(s99) {
    var t5;
    let e4 = s99.state.field(Ft3);
    e4 == null ? this.cursor != null && ((t5 = this.cursor) === null || t5 === void 0 || t5.remove(), this.cursor = null) : (this.cursor || (this.cursor = this.view.scrollDOM.appendChild(document.createElement("div")), this.cursor.className = "cm-dropCursor"), (s99.startState.field(Ft3) != e4 || s99.docChanged || s99.geometryChanged) && this.view.requestMeasure(this.measureReq));
  }
  readPos() {
    let { view: s99 } = this, t5 = s99.state.field(Ft3), e4 = t5 != null && s99.coordsAtPos(t5);
    if (!e4) return null;
    let i9 = s99.scrollDOM.getBoundingClientRect();
    return {
      left: e4.left - i9.left + s99.scrollDOM.scrollLeft * s99.scaleX,
      top: e4.top - i9.top + s99.scrollDOM.scrollTop * s99.scaleY,
      height: e4.bottom - e4.top
    };
  }
  drawCursor(s99) {
    if (this.cursor) {
      let { scaleX: t5, scaleY: e4 } = this.view;
      s99 ? (this.cursor.style.left = s99.left / t5 + "px", this.cursor.style.top = s99.top / e4 + "px", this.cursor.style.height = s99.height / e4 + "px") : this.cursor.style.left = "-100000px";
    }
  }
  destroy() {
    this.cursor && this.cursor.remove();
  }
  setDropPos(s99) {
    this.view.state.field(Ft3) != s99 && this.view.dispatch({
      effects: Xn2.of(s99)
    });
  }
}, {
  eventObservers: {
    dragover(s99) {
      this.setDropPos(this.view.posAtCoords({
        x: s99.clientX,
        y: s99.clientY
      }));
    },
    dragleave(s99) {
      (s99.target == this.view.contentDOM || !this.view.contentDOM.contains(s99.relatedTarget)) && this.setDropPos(null);
    },
    dragend() {
      this.setDropPos(null);
    },
    drop() {
      this.setDropPos(null);
    }
  }
});
function Ws2(s99, t5, e4, i9, n22) {
  t5.lastIndex = 0;
  for (let o4 = s99.iterRange(e4, i9), r2 = e4, l11; !o4.next().done; r2 += o4.value.length) if (!o4.lineBreak) for (; l11 = t5.exec(o4.value); ) n22(r2 + l11.index, l11);
}
function Hr2(s99, t5) {
  let e4 = s99.visibleRanges;
  if (e4.length == 1 && e4[0].from == s99.viewport.from && e4[0].to == s99.viewport.to) return e4;
  let i9 = [];
  for (let { from: n22, to: o4 } of e4) n22 = Math.max(s99.state.doc.lineAt(n22).from, n22 - t5), o4 = Math.min(s99.state.doc.lineAt(o4).to, o4 + t5), i9.length && i9[i9.length - 1].to >= n22 ? i9[i9.length - 1].to = o4 : i9.push({
    from: n22,
    to: o4
  });
  return i9;
}
var ie8 = class {
  constructor(t5) {
    let { regexp: e4, decoration: i9, decorate: n22, boundary: o4, maxLength: r2 = 1e3 } = t5;
    if (!e4.global) throw new RangeError("The regular expression given to MatchDecorator should have its 'g' flag set");
    if (this.regexp = e4, n22) this.addMatch = (l11, a2, h3, c4) => n22(c4, h3, h3 + l11[0].length, l11, a2);
    else if (typeof i9 == "function") this.addMatch = (l11, a2, h3, c4) => {
      let f2 = i9(l11, a2, h3);
      f2 && c4(h3, h3 + l11[0].length, f2);
    };
    else if (i9) this.addMatch = (l11, a2, h3, c4) => c4(h3, h3 + l11[0].length, i9);
    else throw new RangeError("Either 'decorate' or 'decoration' should be provided to MatchDecorator");
    this.boundary = o4, this.maxLength = r2;
  }
  createDeco(t5) {
    let e4 = new re7(), i9 = e4.add.bind(e4);
    for (let { from: n22, to: o4 } of Hr2(t5, this.maxLength)) Ws2(t5.state.doc, this.regexp, n22, o4, (r2, l11) => this.addMatch(l11, t5, r2, i9));
    return e4.finish();
  }
  updateDeco(t5, e4) {
    let i9 = 1e9, n22 = -1;
    return t5.docChanged && t5.changes.iterChanges((o4, r2, l11, a2) => {
      a2 >= t5.view.viewport.from && l11 <= t5.view.viewport.to && (i9 = Math.min(l11, i9), n22 = Math.max(a2, n22));
    }), t5.viewportMoved || n22 - i9 > 1e3 ? this.createDeco(t5.view) : n22 > -1 ? this.updateRange(t5.view, e4.map(t5.changes), i9, n22) : e4;
  }
  updateRange(t5, e4, i9, n22) {
    for (let o4 of t5.visibleRanges) {
      let r2 = Math.max(o4.from, i9), l11 = Math.min(o4.to, n22);
      if (l11 >= r2) {
        let a2 = t5.state.doc.lineAt(r2), h3 = a2.to < l11 ? t5.state.doc.lineAt(l11) : a2, c4 = Math.max(o4.from, a2.from), f2 = Math.min(o4.to, h3.to);
        if (this.boundary) {
          for (; r2 > a2.from; r2--) if (this.boundary.test(a2.text[r2 - 1 - a2.from])) {
            c4 = r2;
            break;
          }
          for (; l11 < h3.to; l11++) if (this.boundary.test(h3.text[l11 - h3.from])) {
            f2 = l11;
            break;
          }
        }
        let d5 = [], u5, p5 = (g6, m9, b9) => d5.push(b9.range(g6, m9));
        if (a2 == h3) for (this.regexp.lastIndex = c4 - a2.from; (u5 = this.regexp.exec(a2.text)) && u5.index < f2 - a2.from; ) this.addMatch(u5, t5, u5.index + a2.from, p5);
        else Ws2(t5.state.doc, this.regexp, c4, f2, (g6, m9) => this.addMatch(m9, t5, g6, p5));
        e4 = e4.update({
          filterFrom: c4,
          filterTo: f2,
          filter: (g6, m9) => g6 < c4 || m9 > f2,
          add: d5
        });
      }
    }
    return e4;
  }
};
var Vi2 = /x/.unicode != null ? "gu" : "g";
var Pr2 = new RegExp(`[\0-\b
-\x7F-\x9F\xAD\u061C\u200B\u200E\u200F\u2028\u2029\u202D\u202E\u2066\u2067\u2069\uFEFF\uFFF9-\uFFFC]`, Vi2);
var Qe5 = null;
function Wr2() {
  var s99;
  if (Qe5 == null && typeof document < "u" && document.body) {
    let t5 = document.body.style;
    Qe5 = ((s99 = t5.tabSize) !== null && s99 !== void 0 ? s99 : t5.MozTabSize) != null;
  }
  return Qe5 || false;
}
var xe8 = k7.define({
  combine(s99) {
    let t5 = rt4(s99, {
      render: null,
      specialChars: Pr2,
      addSpecialChars: null
    });
    return (t5.replaceTabs = !Wr2()) && (t5.specialChars = new RegExp("	|" + t5.specialChars.source, Vi2)), t5.addSpecialChars && (t5.specialChars = new RegExp(t5.specialChars.source + "|" + t5.addSpecialChars.source, Vi2)), t5;
  }
});
var Fs2 = N10.fromClass(class {
  constructor() {
    this.height = 1e3, this.attrs = {
      style: "padding-bottom: 1000px"
    };
  }
  update(s99) {
    let { view: t5 } = s99, e4 = t5.viewState.editorHeight - t5.defaultLineHeight - t5.documentPadding.top - 0.5;
    e4 >= 0 && e4 != this.height && (this.height = e4, this.attrs = {
      style: `padding-bottom: ${e4}px`
    });
  }
});
var zr2 = T8.line({
  class: "cm-activeLine"
});
var qr2 = N10.fromClass(class {
  constructor(s99) {
    this.decorations = this.getDeco(s99);
  }
  update(s99) {
    (s99.docChanged || s99.selectionSet) && (this.decorations = this.getDeco(s99.view));
  }
  getDeco(s99) {
    let t5 = -1, e4 = [];
    for (let i9 of s99.state.selection.ranges) {
      let n22 = s99.lineBlockAt(i9.head);
      n22.from > t5 && (e4.push(zr2.range(n22.from)), t5 = n22.from);
    }
    return T8.set(e4);
  }
}, {
  decorations: (s99) => s99.decorations
});
var ge7 = "-10000px";
var We6 = class {
  constructor(t5, e4, i9, n22) {
    this.facet = e4, this.createTooltipView = i9, this.removeTooltipView = n22, this.input = t5.state.facet(e4), this.tooltips = this.input.filter((r2) => r2);
    let o4 = null;
    this.tooltipViews = this.tooltips.map((r2) => o4 = i9(r2, o4));
  }
  update(t5, e4) {
    var i9;
    let n22 = t5.state.facet(this.facet), o4 = n22.filter((a2) => a2);
    if (n22 === this.input) {
      for (let a2 of this.tooltipViews) a2.update && a2.update(t5);
      return false;
    }
    let r2 = [], l11 = e4 ? [] : null;
    for (let a2 = 0; a2 < o4.length; a2++) {
      let h3 = o4[a2], c4 = -1;
      if (h3) {
        for (let f2 = 0; f2 < this.tooltips.length; f2++) {
          let d5 = this.tooltips[f2];
          d5 && d5.create == h3.create && (c4 = f2);
        }
        if (c4 < 0) r2[a2] = this.createTooltipView(h3, a2 ? r2[a2 - 1] : null), l11 && (l11[a2] = !!h3.above);
        else {
          let f2 = r2[a2] = this.tooltipViews[c4];
          l11 && (l11[a2] = e4[c4]), f2.update && f2.update(t5);
        }
      }
    }
    for (let a2 of this.tooltipViews) r2.indexOf(a2) < 0 && (this.removeTooltipView(a2), (i9 = a2.destroy) === null || i9 === void 0 || i9.call(a2));
    return e4 && (l11.forEach((a2, h3) => e4[h3] = a2), e4.length = l11.length), this.input = n22, this.tooltips = o4, this.tooltipViews = r2, true;
  }
};
function $r2(s99) {
  let t5 = s99.dom.ownerDocument.documentElement;
  return {
    top: 0,
    left: 0,
    bottom: t5.clientHeight,
    right: t5.clientWidth
  };
}
var ve7 = k7.define({
  combine: (s99) => {
    var t5, e4, i9;
    return {
      position: y8.ios ? "absolute" : ((t5 = s99.find((n22) => n22.position)) === null || t5 === void 0 ? void 0 : t5.position) || "fixed",
      parent: ((e4 = s99.find((n22) => n22.parent)) === null || e4 === void 0 ? void 0 : e4.parent) || null,
      tooltipSpace: ((i9 = s99.find((n22) => n22.tooltipSpace)) === null || i9 === void 0 ? void 0 : i9.tooltipSpace) || $r2
    };
  }
});
var zs2 = /* @__PURE__ */ new WeakMap();
var je5 = N10.fromClass(class {
  constructor(s99) {
    this.view = s99, this.above = [], this.inView = true, this.madeAbsolute = false, this.lastTransaction = 0, this.measureTimeout = -1;
    let t5 = s99.state.facet(ve7);
    this.position = t5.position, this.parent = t5.parent, this.classes = s99.themeClasses, this.createContainer(), this.measureReq = {
      read: this.readMeasure.bind(this),
      write: this.writeMeasure.bind(this),
      key: this
    }, this.resizeObserver = typeof ResizeObserver == "function" ? new ResizeObserver(() => this.measureSoon()) : null, this.manager = new We6(s99, $n2, (e4, i9) => this.createTooltip(e4, i9), (e4) => {
      this.resizeObserver && this.resizeObserver.unobserve(e4.dom), e4.dom.remove();
    }), this.above = this.manager.tooltips.map((e4) => !!e4.above), this.intersectionObserver = typeof IntersectionObserver == "function" ? new IntersectionObserver((e4) => {
      Date.now() > this.lastTransaction - 50 && e4.length > 0 && e4[e4.length - 1].intersectionRatio < 1 && this.measureSoon();
    }, {
      threshold: [
        1
      ]
    }) : null, this.observeIntersection(), s99.win.addEventListener("resize", this.measureSoon = this.measureSoon.bind(this)), this.maybeMeasure();
  }
  createContainer() {
    this.parent ? (this.container = document.createElement("div"), this.container.style.position = "relative", this.container.className = this.view.themeClasses, this.parent.appendChild(this.container)) : this.container = this.view.dom;
  }
  observeIntersection() {
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect();
      for (let s99 of this.manager.tooltipViews) this.intersectionObserver.observe(s99.dom);
    }
  }
  measureSoon() {
    this.measureTimeout < 0 && (this.measureTimeout = setTimeout(() => {
      this.measureTimeout = -1, this.maybeMeasure();
    }, 50));
  }
  update(s99) {
    s99.transactions.length && (this.lastTransaction = Date.now());
    let t5 = this.manager.update(s99, this.above);
    t5 && this.observeIntersection();
    let e4 = t5 || s99.geometryChanged, i9 = s99.state.facet(ve7);
    if (i9.position != this.position && !this.madeAbsolute) {
      this.position = i9.position;
      for (let n22 of this.manager.tooltipViews) n22.dom.style.position = this.position;
      e4 = true;
    }
    if (i9.parent != this.parent) {
      this.parent && this.container.remove(), this.parent = i9.parent, this.createContainer();
      for (let n22 of this.manager.tooltipViews) this.container.appendChild(n22.dom);
      e4 = true;
    } else this.parent && this.view.themeClasses != this.classes && (this.classes = this.container.className = this.view.themeClasses);
    e4 && this.maybeMeasure();
  }
  createTooltip(s99, t5) {
    let e4 = s99.create(this.view), i9 = t5 ? t5.dom : null;
    if (e4.dom.classList.add("cm-tooltip"), s99.arrow && !e4.dom.querySelector(".cm-tooltip > .cm-tooltip-arrow")) {
      let n22 = document.createElement("div");
      n22.className = "cm-tooltip-arrow", e4.dom.appendChild(n22);
    }
    return e4.dom.style.position = this.position, e4.dom.style.top = ge7, e4.dom.style.left = "0px", this.container.insertBefore(e4.dom, i9), e4.mount && e4.mount(this.view), this.resizeObserver && this.resizeObserver.observe(e4.dom), e4;
  }
  destroy() {
    var s99, t5, e4;
    this.view.win.removeEventListener("resize", this.measureSoon);
    for (let i9 of this.manager.tooltipViews) i9.dom.remove(), (s99 = i9.destroy) === null || s99 === void 0 || s99.call(i9);
    this.parent && this.container.remove(), (t5 = this.resizeObserver) === null || t5 === void 0 || t5.disconnect(), (e4 = this.intersectionObserver) === null || e4 === void 0 || e4.disconnect(), clearTimeout(this.measureTimeout);
  }
  readMeasure() {
    let s99 = 1, t5 = 1, e4 = false;
    if (this.position == "fixed" && this.manager.tooltipViews.length) {
      let { dom: o4 } = this.manager.tooltipViews[0];
      if (y8.safari) {
        let r2 = o4.getBoundingClientRect();
        e4 = Math.abs(r2.top + 1e4) > 1 || Math.abs(r2.left) > 1;
      } else e4 = !!o4.offsetParent && o4.offsetParent != this.container.ownerDocument.body;
    }
    if (e4 || this.position == "absolute") if (this.parent) {
      let o4 = this.parent.getBoundingClientRect();
      o4.width && o4.height && (s99 = o4.width / this.parent.offsetWidth, t5 = o4.height / this.parent.offsetHeight);
    } else ({ scaleX: s99, scaleY: t5 } = this.view.viewState);
    let i9 = this.view.scrollDOM.getBoundingClientRect(), n22 = os2(this.view);
    return {
      visible: {
        left: i9.left + n22.left,
        top: i9.top + n22.top,
        right: i9.right - n22.right,
        bottom: i9.bottom - n22.bottom
      },
      parent: this.parent ? this.container.getBoundingClientRect() : this.view.dom.getBoundingClientRect(),
      pos: this.manager.tooltips.map((o4, r2) => {
        let l11 = this.manager.tooltipViews[r2];
        return l11.getCoords ? l11.getCoords(o4.pos) : this.view.coordsAtPos(o4.pos);
      }),
      size: this.manager.tooltipViews.map(({ dom: o4 }) => o4.getBoundingClientRect()),
      space: this.view.state.facet(ve7).tooltipSpace(this.view),
      scaleX: s99,
      scaleY: t5,
      makeAbsolute: e4
    };
  }
  writeMeasure(s99) {
    var t5;
    if (s99.makeAbsolute) {
      this.madeAbsolute = true, this.position = "absolute";
      for (let l11 of this.manager.tooltipViews) l11.dom.style.position = "absolute";
    }
    let { visible: e4, space: i9, scaleX: n22, scaleY: o4 } = s99, r2 = [];
    for (let l11 = 0; l11 < this.manager.tooltips.length; l11++) {
      let a2 = this.manager.tooltips[l11], h3 = this.manager.tooltipViews[l11], { dom: c4 } = h3, f2 = s99.pos[l11], d5 = s99.size[l11];
      if (!f2 || a2.clip !== false && (f2.bottom <= Math.max(e4.top, i9.top) || f2.top >= Math.min(e4.bottom, i9.bottom) || f2.right < Math.max(e4.left, i9.left) - 0.1 || f2.left > Math.min(e4.right, i9.right) + 0.1)) {
        c4.style.top = ge7;
        continue;
      }
      let u5 = a2.arrow ? h3.dom.querySelector(".cm-tooltip-arrow") : null, p5 = u5 ? 7 : 0, g6 = d5.right - d5.left, m9 = (t5 = zs2.get(h3)) !== null && t5 !== void 0 ? t5 : d5.bottom - d5.top, b9 = h3.offset || Ur, w11 = this.view.textDirection == R9.LTR, M14 = d5.width > i9.right - i9.left ? w11 ? i9.left : i9.right - d5.width : w11 ? Math.max(i9.left, Math.min(f2.left - (u5 ? 14 : 0) + b9.x, i9.right - g6)) : Math.min(Math.max(i9.left, f2.left - g6 + (u5 ? 14 : 0) - b9.x), i9.right - g6), A11 = this.above[l11];
      !a2.strictSide && (A11 ? f2.top - m9 - p5 - b9.y < i9.top : f2.bottom + m9 + p5 + b9.y > i9.bottom) && A11 == i9.bottom - f2.bottom > f2.top - i9.top && (A11 = this.above[l11] = !A11);
      let v8 = (A11 ? f2.top - i9.top : i9.bottom - f2.bottom) - p5;
      if (v8 < m9 && h3.resize !== false) {
        if (v8 < this.view.defaultLineHeight) {
          c4.style.top = ge7;
          continue;
        }
        zs2.set(h3, m9), c4.style.height = (m9 = v8) / o4 + "px";
      } else c4.style.height && (c4.style.height = "");
      let x11 = A11 ? f2.top - m9 - p5 - b9.y : f2.bottom + p5 + b9.y, L10 = M14 + g6;
      if (h3.overlap !== true) for (let H10 of r2) H10.left < L10 && H10.right > M14 && H10.top < x11 + m9 && H10.bottom > x11 && (x11 = A11 ? H10.top - m9 - 2 - p5 : H10.bottom + p5 + 2);
      if (this.position == "absolute" ? (c4.style.top = (x11 - s99.parent.top) / o4 + "px", qs2(c4, (M14 - s99.parent.left) / n22)) : (c4.style.top = x11 / o4 + "px", qs2(c4, M14 / n22)), u5) {
        let H10 = f2.left + (w11 ? b9.x : -b9.x) - (M14 + 14 - 7);
        u5.style.left = H10 / n22 + "px";
      }
      h3.overlap !== true && r2.push({
        left: M14,
        top: x11,
        right: L10,
        bottom: x11 + m9
      }), c4.classList.toggle("cm-tooltip-above", A11), c4.classList.toggle("cm-tooltip-below", !A11), h3.positioned && h3.positioned(s99.space);
    }
  }
  maybeMeasure() {
    if (this.manager.tooltips.length && (this.view.inView && this.view.requestMeasure(this.measureReq), this.inView != this.view.inView && (this.inView = this.view.inView, !this.inView))) for (let s99 of this.manager.tooltipViews) s99.dom.style.top = ge7;
  }
}, {
  eventObservers: {
    scroll() {
      this.maybeMeasure();
    }
  }
});
function qs2(s99, t5) {
  let e4 = parseInt(s99.style.left, 10);
  (isNaN(e4) || Math.abs(t5 - e4) > 1) && (s99.style.left = t5 + "px");
}
var Gr2 = k8.baseTheme({
  ".cm-tooltip": {
    zIndex: 500,
    boxSizing: "border-box"
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
var Ur = {
  x: 0,
  y: 0
};
var $n2 = k7.define({
  enables: [
    je5,
    Gr2
  ]
});
var se9 = k7.define({
  combine: (s99) => s99.reduce((t5, e4) => t5.concat(e4), [])
});
var Ve5 = class s88 {
  static create(t5) {
    return new s88(t5);
  }
  constructor(t5) {
    this.view = t5, this.mounted = false, this.dom = document.createElement("div"), this.dom.classList.add("cm-tooltip-hover"), this.manager = new We6(t5, se9, (e4, i9) => this.createHostedView(e4, i9), (e4) => e4.dom.remove());
  }
  createHostedView(t5, e4) {
    let i9 = t5.create(this.view);
    return i9.dom.classList.add("cm-tooltip-section"), this.dom.insertBefore(i9.dom, e4 ? e4.dom.nextSibling : this.dom.firstChild), this.mounted && i9.mount && i9.mount(this.view), i9;
  }
  mount(t5) {
    for (let e4 of this.manager.tooltipViews) e4.mount && e4.mount(t5);
    this.mounted = true;
  }
  positioned(t5) {
    for (let e4 of this.manager.tooltipViews) e4.positioned && e4.positioned(t5);
  }
  update(t5) {
    this.manager.update(t5);
  }
  destroy() {
    var t5;
    for (let e4 of this.manager.tooltipViews) (t5 = e4.destroy) === null || t5 === void 0 || t5.call(e4);
  }
  passProp(t5) {
    let e4;
    for (let i9 of this.manager.tooltipViews) {
      let n22 = i9[t5];
      if (n22 !== void 0) {
        if (e4 === void 0) e4 = n22;
        else if (e4 !== n22) return;
      }
    }
    return e4;
  }
  get offset() {
    return this.passProp("offset");
  }
  get getCoords() {
    return this.passProp("getCoords");
  }
  get overlap() {
    return this.passProp("overlap");
  }
  get resize() {
    return this.passProp("resize");
  }
};
var Qr2 = $n2.compute([
  se9
], (s99) => {
  let t5 = s99.facet(se9);
  return t5.length === 0 ? null : {
    pos: Math.min(...t5.map((e4) => e4.pos)),
    end: Math.max(...t5.map((e4) => {
      var i9;
      return (i9 = e4.end) !== null && i9 !== void 0 ? i9 : e4.pos;
    })),
    create: Ve5.create,
    above: t5[0].above,
    arrow: t5.some((e4) => e4.arrow)
  };
});
function Bl(s99, t5) {
  let e4 = s99.plugin(je5);
  if (!e4) return null;
  let i9 = e4.manager.tooltips.indexOf(t5);
  return i9 < 0 ? null : e4.manager.tooltipViews[i9];
}
var Gn2 = v5.define();
var Hl = Gn2.of(null);
var _i2 = k7.define({
  combine(s99) {
    let t5, e4;
    for (let i9 of s99) t5 = t5 || i9.topContainer, e4 = e4 || i9.bottomContainer;
    return {
      topContainer: t5,
      bottomContainer: e4
    };
  }
});
var Un2 = N10.fromClass(class {
  constructor(s99) {
    this.input = s99.state.facet(ji2), this.specs = this.input.filter((e4) => e4), this.panels = this.specs.map((e4) => e4(s99));
    let t5 = s99.state.facet(_i2);
    this.top = new Mt5(s99, true, t5.topContainer), this.bottom = new Mt5(s99, false, t5.bottomContainer), this.top.sync(this.panels.filter((e4) => e4.top)), this.bottom.sync(this.panels.filter((e4) => !e4.top));
    for (let e4 of this.panels) e4.dom.classList.add("cm-panel"), e4.mount && e4.mount();
  }
  update(s99) {
    let t5 = s99.state.facet(_i2);
    this.top.container != t5.topContainer && (this.top.sync([]), this.top = new Mt5(s99.view, true, t5.topContainer)), this.bottom.container != t5.bottomContainer && (this.bottom.sync([]), this.bottom = new Mt5(s99.view, false, t5.bottomContainer)), this.top.syncClasses(), this.bottom.syncClasses();
    let e4 = s99.state.facet(ji2);
    if (e4 != this.input) {
      let i9 = e4.filter((a2) => a2), n22 = [], o4 = [], r2 = [], l11 = [];
      for (let a2 of i9) {
        let h3 = this.specs.indexOf(a2), c4;
        h3 < 0 ? (c4 = a2(s99.view), l11.push(c4)) : (c4 = this.panels[h3], c4.update && c4.update(s99)), n22.push(c4), (c4.top ? o4 : r2).push(c4);
      }
      this.specs = i9, this.panels = n22, this.top.sync(o4), this.bottom.sync(r2);
      for (let a2 of l11) a2.dom.classList.add("cm-panel"), a2.mount && a2.mount();
    } else for (let i9 of this.panels) i9.update && i9.update(s99);
  }
  destroy() {
    this.top.sync([]), this.bottom.sync([]);
  }
}, {
  provide: (s99) => k8.scrollMargins.of((t5) => {
    let e4 = t5.plugin(s99);
    return e4 && {
      top: e4.top.scrollMargin(),
      bottom: e4.bottom.scrollMargin()
    };
  })
});
var Mt5 = class {
  constructor(t5, e4, i9) {
    this.view = t5, this.top = e4, this.container = i9, this.dom = void 0, this.classes = "", this.panels = [], this.syncClasses();
  }
  sync(t5) {
    for (let e4 of this.panels) e4.destroy && t5.indexOf(e4) < 0 && e4.destroy();
    this.panels = t5, this.syncDOM();
  }
  syncDOM() {
    if (this.panels.length == 0) {
      this.dom && (this.dom.remove(), this.dom = void 0);
      return;
    }
    if (!this.dom) {
      this.dom = document.createElement("div"), this.dom.className = this.top ? "cm-panels cm-panels-top" : "cm-panels cm-panels-bottom", this.dom.style[this.top ? "top" : "bottom"] = "0";
      let e4 = this.container || this.view.dom;
      e4.insertBefore(this.dom, this.top ? e4.firstChild : null);
    }
    let t5 = this.dom.firstChild;
    for (let e4 of this.panels) if (e4.dom.parentNode == this.dom) {
      for (; t5 != e4.dom; ) t5 = Ks2(t5);
      t5 = t5.nextSibling;
    } else this.dom.insertBefore(e4.dom, t5);
    for (; t5; ) t5 = Ks2(t5);
  }
  scrollMargin() {
    return !this.dom || this.container ? 0 : Math.max(0, this.top ? this.dom.getBoundingClientRect().bottom - Math.max(0, this.view.scrollDOM.getBoundingClientRect().top) : Math.min(innerHeight, this.view.scrollDOM.getBoundingClientRect().bottom) - this.dom.getBoundingClientRect().top);
  }
  syncClasses() {
    if (!(!this.container || this.classes == this.view.themeClasses)) {
      for (let t5 of this.classes.split(" ")) t5 && this.container.classList.remove(t5);
      for (let t5 of (this.classes = this.view.themeClasses).split(" ")) t5 && this.container.classList.add(t5);
    }
  }
};
function Ks2(s99) {
  let t5 = s99.nextSibling;
  return s99.remove(), t5;
}
var ji2 = k7.define({
  enables: Un2
});
var Se8 = z8.define({
  create() {
    return [];
  },
  update(s99, t5) {
    for (let e4 of t5.effects) e4.is(Qn2) ? s99 = [
      e4.value
    ].concat(s99) : e4.is(Jn2) && (s99 = s99.filter((i9) => i9 != e4.value));
    return s99;
  },
  provide: (s99) => ji2.computeN([
    s99
  ], (t5) => t5.field(s99))
});
var Qn2 = v5.define();
var Jn2 = v5.define();
var Q9 = class extends q7 {
  compare(t5) {
    return this == t5 || this.constructor == t5.constructor && this.eq(t5);
  }
  eq(t5) {
    return false;
  }
  destroy(t5) {
  }
};
Q9.prototype.elementClass = "";
Q9.prototype.toDOM = void 0;
Q9.prototype.mapMode = E6.TrackBefore;
Q9.prototype.startSide = Q9.prototype.endSide = -1;
Q9.prototype.point = true;
var Ce8 = k7.define();
var il = k7.define();
var sl = {
  class: "",
  renderEmptyElements: false,
  elementStyle: "",
  markers: () => T7.empty,
  lineMarker: () => null,
  widgetMarker: () => null,
  lineMarkerChange: null,
  initialSpacer: null,
  updateSpacer: null,
  domEventHandlers: {},
  side: "before"
};
var $t3 = k7.define();
function Fl(s99) {
  return [
    Zn2(),
    $t3.of({
      ...sl,
      ...s99
    })
  ];
}
var Yi2 = k7.define({
  combine: (s99) => s99.some((t5) => t5)
});
function Zn2(s99) {
  let t5 = [
    nl
  ];
  return s99 && s99.fixed === false && t5.push(Yi2.of(true)), t5;
}
var nl = N10.fromClass(class {
  constructor(s99) {
    this.view = s99, this.domAfter = null, this.prevViewport = s99.viewport, this.dom = document.createElement("div"), this.dom.className = "cm-gutters cm-gutters-before", this.dom.setAttribute("aria-hidden", "true"), this.dom.style.minHeight = this.view.contentHeight / this.view.scaleY + "px", this.gutters = s99.state.facet($t3).map((t5) => new Fe7(s99, t5)), this.fixed = !s99.state.facet(Yi2);
    for (let t5 of this.gutters) t5.config.side == "after" ? this.getDOMAfter().appendChild(t5.dom) : this.dom.appendChild(t5.dom);
    this.fixed && (this.dom.style.position = "sticky"), this.syncGutters(false), s99.scrollDOM.insertBefore(this.dom, s99.contentDOM);
  }
  getDOMAfter() {
    return this.domAfter || (this.domAfter = document.createElement("div"), this.domAfter.className = "cm-gutters cm-gutters-after", this.domAfter.setAttribute("aria-hidden", "true"), this.domAfter.style.minHeight = this.view.contentHeight / this.view.scaleY + "px", this.domAfter.style.position = this.fixed ? "sticky" : "", this.view.scrollDOM.appendChild(this.domAfter)), this.domAfter;
  }
  update(s99) {
    if (this.updateGutters(s99)) {
      let t5 = this.prevViewport, e4 = s99.view.viewport, i9 = Math.min(t5.to, e4.to) - Math.max(t5.from, e4.from);
      this.syncGutters(i9 < (e4.to - e4.from) * 0.8);
    }
    if (s99.geometryChanged) {
      let t5 = this.view.contentHeight / this.view.scaleY + "px";
      this.dom.style.minHeight = t5, this.domAfter && (this.domAfter.style.minHeight = t5);
    }
    this.view.state.facet(Yi2) != !this.fixed && (this.fixed = !this.fixed, this.dom.style.position = this.fixed ? "sticky" : "", this.domAfter && (this.domAfter.style.position = this.fixed ? "sticky" : "")), this.prevViewport = s99.view.viewport;
  }
  syncGutters(s99) {
    let t5 = this.dom.nextSibling;
    s99 && (this.dom.remove(), this.domAfter && this.domAfter.remove());
    let e4 = T7.iter(this.view.state.facet(Ce8), this.view.viewport.from), i9 = [], n22 = this.gutters.map((o4) => new $i2(o4, this.view.viewport, -this.view.documentPadding.top));
    for (let o4 of this.view.viewportLineBlocks) if (i9.length && (i9 = []), Array.isArray(o4.type)) {
      let r2 = true;
      for (let l11 of o4.type) if (l11.type == P8.Text && r2) {
        Xi2(e4, i9, l11.from);
        for (let a2 of n22) a2.line(this.view, l11, i9);
        r2 = false;
      } else if (l11.widget) for (let a2 of n22) a2.widget(this.view, l11);
    } else if (o4.type == P8.Text) {
      Xi2(e4, i9, o4.from);
      for (let r2 of n22) r2.line(this.view, o4, i9);
    } else if (o4.widget) for (let r2 of n22) r2.widget(this.view, o4);
    for (let o4 of n22) o4.finish();
    s99 && (this.view.scrollDOM.insertBefore(this.dom, t5), this.domAfter && this.view.scrollDOM.appendChild(this.domAfter));
  }
  updateGutters(s99) {
    let t5 = s99.startState.facet($t3), e4 = s99.state.facet($t3), i9 = s99.docChanged || s99.heightChanged || s99.viewportChanged || !T7.eq(s99.startState.facet(Ce8), s99.state.facet(Ce8), s99.view.viewport.from, s99.view.viewport.to);
    if (t5 == e4) for (let n22 of this.gutters) n22.update(s99) && (i9 = true);
    else {
      i9 = true;
      let n22 = [];
      for (let o4 of e4) {
        let r2 = t5.indexOf(o4);
        r2 < 0 ? n22.push(new Fe7(this.view, o4)) : (this.gutters[r2].update(s99), n22.push(this.gutters[r2]));
      }
      for (let o4 of this.gutters) o4.dom.remove(), n22.indexOf(o4) < 0 && o4.destroy();
      for (let o4 of n22) o4.config.side == "after" ? this.getDOMAfter().appendChild(o4.dom) : this.dom.appendChild(o4.dom);
      this.gutters = n22;
    }
    return i9;
  }
  destroy() {
    for (let s99 of this.gutters) s99.destroy();
    this.dom.remove(), this.domAfter && this.domAfter.remove();
  }
}, {
  provide: (s99) => k8.scrollMargins.of((t5) => {
    let e4 = t5.plugin(s99);
    if (!e4 || e4.gutters.length == 0 || !e4.fixed) return null;
    let i9 = e4.dom.offsetWidth * t5.scaleX, n22 = e4.domAfter ? e4.domAfter.offsetWidth * t5.scaleX : 0;
    return t5.textDirection == R9.LTR ? {
      left: i9,
      right: n22
    } : {
      right: i9,
      left: n22
    };
  })
});
function _s2(s99) {
  return Array.isArray(s99) ? s99 : [
    s99
  ];
}
function Xi2(s99, t5, e4) {
  for (; s99.value && s99.from <= e4; ) s99.from == e4 && t5.push(s99.value), s99.next();
}
var $i2 = class {
  constructor(t5, e4, i9) {
    this.gutter = t5, this.height = i9, this.i = 0, this.cursor = T7.iter(t5.markers, e4.from);
  }
  addElement(t5, e4, i9) {
    let { gutter: n22 } = this, o4 = (e4.top - this.height) / t5.scaleY, r2 = e4.height / t5.scaleY;
    if (this.i == n22.elements.length) {
      let l11 = new Ie7(t5, r2, o4, i9);
      n22.elements.push(l11), n22.dom.appendChild(l11.dom);
    } else n22.elements[this.i].update(t5, r2, o4, i9);
    this.height = e4.bottom, this.i++;
  }
  line(t5, e4, i9) {
    let n22 = [];
    Xi2(this.cursor, n22, e4.from), i9.length && (n22 = n22.concat(i9));
    let o4 = this.gutter.config.lineMarker(t5, e4, n22);
    o4 && n22.unshift(o4);
    let r2 = this.gutter;
    n22.length == 0 && !r2.config.renderEmptyElements || this.addElement(t5, e4, n22);
  }
  widget(t5, e4) {
    let i9 = this.gutter.config.widgetMarker(t5, e4.widget, e4), n22 = i9 ? [
      i9
    ] : null;
    for (let o4 of t5.state.facet(il)) {
      let r2 = o4(t5, e4.widget, e4);
      r2 && (n22 || (n22 = [])).push(r2);
    }
    n22 && this.addElement(t5, e4, n22);
  }
  finish() {
    let t5 = this.gutter;
    for (; t5.elements.length > this.i; ) {
      let e4 = t5.elements.pop();
      t5.dom.removeChild(e4.dom), e4.destroy();
    }
  }
};
var Fe7 = class {
  constructor(t5, e4) {
    this.view = t5, this.config = e4, this.elements = [], this.spacer = null, this.dom = document.createElement("div"), this.dom.className = "cm-gutter" + (this.config.class ? " " + this.config.class : "");
    for (let i9 in e4.domEventHandlers) this.dom.addEventListener(i9, (n22) => {
      let o4 = n22.target, r2;
      if (o4 != this.dom && this.dom.contains(o4)) {
        for (; o4.parentNode != this.dom; ) o4 = o4.parentNode;
        let a2 = o4.getBoundingClientRect();
        r2 = (a2.top + a2.bottom) / 2;
      } else r2 = n22.clientY;
      let l11 = t5.lineBlockAtHeight(r2 - t5.documentTop);
      e4.domEventHandlers[i9](t5, l11, n22) && n22.preventDefault();
    });
    this.markers = _s2(e4.markers(t5)), e4.initialSpacer && (this.spacer = new Ie7(t5, 0, 0, [
      e4.initialSpacer(t5)
    ]), this.dom.appendChild(this.spacer.dom), this.spacer.dom.style.cssText += "visibility: hidden; pointer-events: none");
  }
  update(t5) {
    let e4 = this.markers;
    if (this.markers = _s2(this.config.markers(t5.view)), this.spacer && this.config.updateSpacer) {
      let n22 = this.config.updateSpacer(this.spacer.markers[0], t5);
      n22 != this.spacer.markers[0] && this.spacer.update(t5.view, 0, 0, [
        n22
      ]);
    }
    let i9 = t5.view.viewport;
    return !T7.eq(this.markers, e4, i9.from, i9.to) || (this.config.lineMarkerChange ? this.config.lineMarkerChange(t5) : false);
  }
  destroy() {
    for (let t5 of this.elements) t5.destroy();
  }
};
var Ie7 = class {
  constructor(t5, e4, i9, n22) {
    this.height = -1, this.above = 0, this.markers = [], this.dom = document.createElement("div"), this.dom.className = "cm-gutterElement", this.update(t5, e4, i9, n22);
  }
  update(t5, e4, i9, n22) {
    this.height != e4 && (this.height = e4, this.dom.style.height = e4 + "px"), this.above != i9 && (this.dom.style.marginTop = (this.above = i9) ? i9 + "px" : ""), ol(this.markers, n22) || this.setMarkers(t5, n22);
  }
  setMarkers(t5, e4) {
    let i9 = "cm-gutterElement", n22 = this.dom.firstChild;
    for (let o4 = 0, r2 = 0; ; ) {
      let l11 = r2, a2 = o4 < e4.length ? e4[o4++] : null, h3 = false;
      if (a2) {
        let c4 = a2.elementClass;
        c4 && (i9 += " " + c4);
        for (let f2 = r2; f2 < this.markers.length; f2++) if (this.markers[f2].compare(a2)) {
          l11 = f2, h3 = true;
          break;
        }
      } else l11 = this.markers.length;
      for (; r2 < l11; ) {
        let c4 = this.markers[r2++];
        if (c4.toDOM) {
          c4.destroy(n22);
          let f2 = n22.nextSibling;
          n22.remove(), n22 = f2;
        }
      }
      if (!a2) break;
      a2.toDOM && (h3 ? n22 = n22.nextSibling : this.dom.insertBefore(a2.toDOM(t5), n22)), h3 && r2++;
    }
    this.dom.className = i9, this.markers = e4;
  }
  destroy() {
    this.setMarkers(null, []);
  }
};
function ol(s99, t5) {
  if (s99.length != t5.length) return false;
  for (let e4 = 0; e4 < s99.length; e4++) if (!s99[e4].compare(t5[e4])) return false;
  return true;
}
var rl = k7.define();
var ll = k7.define();
var kt4 = k7.define({
  combine(s99) {
    return rt4(s99, {
      formatNumber: String,
      domEventHandlers: {}
    }, {
      domEventHandlers(t5, e4) {
        let i9 = Object.assign({}, t5);
        for (let n22 in e4) {
          let o4 = i9[n22], r2 = e4[n22];
          i9[n22] = o4 ? (l11, a2, h3) => o4(l11, a2, h3) || r2(l11, a2, h3) : r2;
        }
        return i9;
      }
    });
  }
});
var Gt3 = class extends Q9 {
  constructor(t5) {
    super(), this.number = t5;
  }
  eq(t5) {
    return this.number == t5.number;
  }
  toDOM() {
    return document.createTextNode(this.number);
  }
};
function Je6(s99, t5) {
  return s99.state.facet(kt4).formatNumber(t5, s99.state);
}
var al = $t3.compute([
  kt4
], (s99) => ({
  class: "cm-lineNumbers",
  renderEmptyElements: false,
  markers(t5) {
    return t5.state.facet(rl);
  },
  lineMarker(t5, e4, i9) {
    return i9.some((n22) => n22.toDOM) ? null : new Gt3(Je6(t5, t5.state.doc.lineAt(e4.from).number));
  },
  widgetMarker: (t5, e4, i9) => {
    for (let n22 of t5.state.facet(ll)) {
      let o4 = n22(t5, e4, i9);
      if (o4) return o4;
    }
    return null;
  },
  lineMarkerChange: (t5) => t5.startState.facet(kt4) != t5.state.facet(kt4),
  initialSpacer(t5) {
    return new Gt3(Je6(t5, js2(t5.state.doc.lines)));
  },
  updateSpacer(t5, e4) {
    let i9 = Je6(e4.view, js2(e4.view.state.doc.lines));
    return i9 == t5.number ? t5 : new Gt3(i9);
  },
  domEventHandlers: s99.facet(kt4).domEventHandlers,
  side: "before"
}));
function js2(s99) {
  let t5 = 9;
  for (; t5 < s99; ) t5 = t5 * 10 + 9;
  return t5;
}
var hl = new class extends Q9 {
  constructor() {
    super(...arguments), this.elementClass = "cm-activeLineGutter";
  }
}();
var cl = Ce8.compute([
  "selection"
], (s99) => {
  let t5 = [], e4 = -1;
  for (let i9 of s99.selection.ranges) {
    let n22 = s99.doc.lineAt(i9.head).from;
    n22 > e4 && (e4 = n22, t5.push(hl.range(n22)));
  }
  return T7.of(t5);
});
function to2(s99) {
  return N10.define((t5) => ({
    decorations: s99.createDeco(t5),
    update(e4) {
      this.decorations = s99.updateDeco(e4, this.decorations);
    }
  }), {
    decorations: (t5) => t5.decorations
  });
}
var fl = T8.mark({
  class: "cm-highlightTab"
});
var dl = T8.mark({
  class: "cm-highlightSpace"
});
var ul = to2(new ie8({
  regexp: /\t| /g,
  decoration: (s99) => s99[0] == "	" ? fl : dl,
  boundary: /\S/
}));
var pl = to2(new ie8({
  regexp: /\s+$/g,
  decoration: T8.mark({
    class: "cm-trailingSpace"
  })
}));

// deno:https://esm.sh/@lezer/common@1.5.0/denonext/common.mjs
var Ie8 = 0;
var I9 = class {
  constructor(e4, t5) {
    this.from = e4, this.to = t5;
  }
};
var v6 = class {
  constructor(e4 = {}) {
    this.id = Ie8++, this.perNode = !!e4.perNode, this.deserialize = e4.deserialize || (() => {
      throw new Error("This node type doesn't define a deserialize function");
    }), this.combine = e4.combine || null;
  }
  add(e4) {
    if (this.perNode) throw new RangeError("Can't add per-node props to node types");
    return typeof e4 != "function" && (e4 = M10.match(e4)), (t5) => {
      let r2 = e4(t5);
      return r2 === void 0 ? null : [
        this,
        r2
      ];
    };
  }
};
v6.closedBy = new v6({
  deserialize: (s99) => s99.split(" ")
});
v6.openedBy = new v6({
  deserialize: (s99) => s99.split(" ")
});
v6.group = new v6({
  deserialize: (s99) => s99.split(" ")
});
v6.isolate = new v6({
  deserialize: (s99) => {
    if (s99 && s99 != "rtl" && s99 != "ltr" && s99 != "auto") throw new RangeError("Invalid value for isolate: " + s99);
    return s99 || "auto";
  }
});
v6.contextHash = new v6({
  perNode: true
});
v6.lookAhead = new v6({
  perNode: true
});
v6.mounted = new v6({
  perNode: true
});
var W9 = class {
  constructor(e4, t5, r2, n22 = false) {
    this.tree = e4, this.overlay = t5, this.parser = r2, this.bracketed = n22;
  }
  static get(e4) {
    return e4 && e4.props && e4.props[v6.mounted.id];
  }
};
var Pe9 = /* @__PURE__ */ Object.create(null);
var M10 = class s89 {
  constructor(e4, t5, r2, n22 = 0) {
    this.name = e4, this.props = t5, this.id = r2, this.flags = n22;
  }
  static define(e4) {
    let t5 = e4.props && e4.props.length ? /* @__PURE__ */ Object.create(null) : Pe9, r2 = (e4.top ? 1 : 0) | (e4.skipped ? 2 : 0) | (e4.error ? 4 : 0) | (e4.name == null ? 8 : 0), n22 = new s89(e4.name || "", t5, e4.id, r2);
    if (e4.props) {
      for (let i9 of e4.props) if (Array.isArray(i9) || (i9 = i9(n22)), i9) {
        if (i9[0].perNode) throw new RangeError("Can't store a per-node prop on a node type");
        t5[i9[0].id] = i9[1];
      }
    }
    return n22;
  }
  prop(e4) {
    return this.props[e4.id];
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
  is(e4) {
    if (typeof e4 == "string") {
      if (this.name == e4) return true;
      let t5 = this.prop(v6.group);
      return t5 ? t5.indexOf(e4) > -1 : false;
    }
    return this.id == e4;
  }
  static match(e4) {
    let t5 = /* @__PURE__ */ Object.create(null);
    for (let r2 in e4) for (let n22 of r2.split(" ")) t5[n22] = e4[r2];
    return (r2) => {
      for (let n22 = r2.prop(v6.group), i9 = -1; i9 < (n22 ? n22.length : 0); i9++) {
        let l11 = t5[i9 < 0 ? r2.name : n22[i9]];
        if (l11) return l11;
      }
    };
  }
};
M10.none = new M10("", /* @__PURE__ */ Object.create(null), 0, 8);
var ye8 = class s90 {
  constructor(e4) {
    this.types = e4;
    for (let t5 = 0; t5 < e4.length; t5++) if (e4[t5].id != t5) throw new RangeError("Node type ids should correspond to array positions when creating a node set");
  }
  extend(...e4) {
    let t5 = [];
    for (let r2 of this.types) {
      let n22 = null;
      for (let i9 of e4) {
        let l11 = i9(r2);
        if (l11) {
          n22 || (n22 = Object.assign({}, r2.props));
          let f2 = l11[1], h3 = l11[0];
          h3.combine && h3.id in n22 && (f2 = h3.combine(n22[h3.id], f2)), n22[h3.id] = f2;
        }
      }
      t5.push(n22 ? new M10(r2.name, n22, r2.id, r2.flags) : r2);
    }
    return new s90(t5);
  }
};
var Z10 = /* @__PURE__ */ new WeakMap();
var xe9 = /* @__PURE__ */ new WeakMap();
var w9;
(function(s99) {
  s99[s99.ExcludeBuffers = 1] = "ExcludeBuffers", s99[s99.IncludeAnonymous = 2] = "IncludeAnonymous", s99[s99.IgnoreMounts = 4] = "IgnoreMounts", s99[s99.IgnoreOverlays = 8] = "IgnoreOverlays", s99[s99.EnterBracketed = 16] = "EnterBracketed";
})(w9 || (w9 = {}));
var E7 = class s91 {
  constructor(e4, t5, r2, n22, i9) {
    if (this.type = e4, this.children = t5, this.positions = r2, this.length = n22, this.props = null, i9 && i9.length) {
      this.props = /* @__PURE__ */ Object.create(null);
      for (let [l11, f2] of i9) this.props[typeof l11 == "number" ? l11 : l11.id] = f2;
    }
  }
  toString() {
    let e4 = W9.get(this);
    if (e4 && !e4.overlay) return e4.tree.toString();
    let t5 = "";
    for (let r2 of this.children) {
      let n22 = r2.toString();
      n22 && (t5 && (t5 += ","), t5 += n22);
    }
    return this.type.name ? (/\W/.test(this.type.name) && !this.type.isError ? JSON.stringify(this.type.name) : this.type.name) + (t5.length ? "(" + t5 + ")" : "") : t5;
  }
  cursor(e4 = 0) {
    return new q9(this.topNode, e4);
  }
  cursorAt(e4, t5 = 0, r2 = 0) {
    let n22 = Z10.get(this) || this.topNode, i9 = new q9(n22);
    return i9.moveTo(e4, t5), Z10.set(this, i9._tree), i9;
  }
  get topNode() {
    return new P9(this, 0, 0, null);
  }
  resolve(e4, t5 = 0) {
    let r2 = Q10(Z10.get(this) || this.topNode, e4, t5, false);
    return Z10.set(this, r2), r2;
  }
  resolveInner(e4, t5 = 0) {
    let r2 = Q10(xe9.get(this) || this.topNode, e4, t5, true);
    return xe9.set(this, r2), r2;
  }
  resolveStack(e4, t5 = 0) {
    return Ee7(this, e4, t5);
  }
  iterate(e4) {
    let { enter: t5, leave: r2, from: n22 = 0, to: i9 = this.length } = e4, l11 = e4.mode || 0, f2 = (l11 & w9.IncludeAnonymous) > 0;
    for (let h3 = this.cursor(l11 | w9.IncludeAnonymous); ; ) {
      let o4 = false;
      if (h3.from <= i9 && h3.to >= n22 && (!f2 && h3.type.isAnonymous || t5(h3) !== false)) {
        if (h3.firstChild()) continue;
        o4 = true;
      }
      for (; o4 && r2 && (f2 || !h3.type.isAnonymous) && r2(h3), !h3.nextSibling(); ) {
        if (!h3.parent()) return;
        o4 = true;
      }
    }
  }
  prop(e4) {
    return e4.perNode ? this.props ? this.props[e4.id] : void 0 : this.type.prop(e4);
  }
  get propValues() {
    let e4 = [];
    if (this.props) for (let t5 in this.props) e4.push([
      +t5,
      this.props[t5]
    ]);
    return e4;
  }
  balance(e4 = {}) {
    return this.children.length <= 8 ? this : ge8(M10.none, this.children, this.positions, 0, this.children.length, 0, this.length, (t5, r2, n22) => new s91(this.type, t5, r2, n22, this.propValues), e4.makeTree || ((t5, r2, n22) => new s91(M10.none, t5, r2, n22)));
  }
  static build(e4) {
    return Oe7(e4);
  }
};
E7.empty = new E7(M10.none, [], [], 0);
var se10 = class s92 {
  constructor(e4, t5) {
    this.buffer = e4, this.index = t5;
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
    return new s92(this.buffer, this.index);
  }
};
var H8 = class s93 {
  constructor(e4, t5, r2) {
    this.buffer = e4, this.length = t5, this.set = r2;
  }
  get type() {
    return M10.none;
  }
  toString() {
    let e4 = [];
    for (let t5 = 0; t5 < this.buffer.length; ) e4.push(this.childString(t5)), t5 = this.buffer[t5 + 3];
    return e4.join(",");
  }
  childString(e4) {
    let t5 = this.buffer[e4], r2 = this.buffer[e4 + 3], n22 = this.set.types[t5], i9 = n22.name;
    if (/\W/.test(i9) && !n22.isError && (i9 = JSON.stringify(i9)), e4 += 4, r2 == e4) return i9;
    let l11 = [];
    for (; e4 < r2; ) l11.push(this.childString(e4)), e4 = this.buffer[e4 + 3];
    return i9 + "(" + l11.join(",") + ")";
  }
  findChild(e4, t5, r2, n22, i9) {
    let { buffer: l11 } = this, f2 = -1;
    for (let h3 = e4; h3 != t5 && !(Ne6(i9, n22, l11[h3 + 1], l11[h3 + 2]) && (f2 = h3, r2 > 0)); h3 = l11[h3 + 3]) ;
    return f2;
  }
  slice(e4, t5, r2) {
    let n22 = this.buffer, i9 = new Uint16Array(t5 - e4), l11 = 0;
    for (let f2 = e4, h3 = 0; f2 < t5; ) {
      i9[h3++] = n22[f2++], i9[h3++] = n22[f2++] - r2;
      let o4 = i9[h3++] = n22[f2++] - r2;
      i9[h3++] = n22[f2++] - e4, l11 = Math.max(l11, o4);
    }
    return new s93(i9, l11, this.set);
  }
};
function Ne6(s99, e4, t5, r2) {
  switch (s99) {
    case -2:
      return t5 < e4;
    case -1:
      return r2 >= e4 && t5 < e4;
    case 0:
      return t5 < e4 && r2 > e4;
    case 1:
      return t5 <= e4 && r2 > e4;
    case 2:
      return r2 > e4;
    case 4:
      return true;
  }
}
function Q10(s99, e4, t5, r2) {
  for (var n22; s99.from == s99.to || (t5 < 1 ? s99.from >= e4 : s99.from > e4) || (t5 > -1 ? s99.to <= e4 : s99.to < e4); ) {
    let l11 = !r2 && s99 instanceof P9 && s99.index < 0 ? null : s99.parent;
    if (!l11) return s99;
    s99 = l11;
  }
  let i9 = r2 ? 0 : w9.IgnoreOverlays;
  if (r2) for (let l11 = s99, f2 = l11.parent; f2; l11 = f2, f2 = l11.parent) l11 instanceof P9 && l11.index < 0 && ((n22 = f2.enter(e4, t5, i9)) === null || n22 === void 0 ? void 0 : n22.from) != l11.from && (s99 = f2);
  for (; ; ) {
    let l11 = s99.enter(e4, t5, i9);
    if (!l11) return s99;
    s99 = l11;
  }
}
var te9 = class {
  cursor(e4 = 0) {
    return new q9(this, e4);
  }
  getChild(e4, t5 = null, r2 = null) {
    let n22 = we7(this, e4, t5, r2);
    return n22.length ? n22[0] : null;
  }
  getChildren(e4, t5 = null, r2 = null) {
    return we7(this, e4, t5, r2);
  }
  resolve(e4, t5 = 0) {
    return Q10(this, e4, t5, false);
  }
  resolveInner(e4, t5 = 0) {
    return Q10(this, e4, t5, true);
  }
  matchContext(e4) {
    return le8(this.parent, e4);
  }
  enterUnfinishedNodesBefore(e4) {
    let t5 = this.childBefore(e4), r2 = this;
    for (; t5; ) {
      let n22 = t5.lastChild;
      if (!n22 || n22.to != t5.to) break;
      n22.type.isError && n22.from == n22.to ? (r2 = t5, t5 = n22.prevSibling) : t5 = n22;
    }
    return r2;
  }
  get node() {
    return this;
  }
  get next() {
    return this.parent;
  }
};
var P9 = class s94 extends te9 {
  constructor(e4, t5, r2, n22) {
    super(), this._tree = e4, this.from = t5, this.index = r2, this._parent = n22;
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
  nextChild(e4, t5, r2, n22, i9 = 0) {
    var l11;
    for (let f2 = this; ; ) {
      for (let { children: h3, positions: o4 } = f2._tree, u5 = t5 > 0 ? h3.length : -1; e4 != u5; e4 += t5) {
        let p5 = h3[e4], d5 = o4[e4] + f2.from;
        if (!(!(i9 & w9.EnterBracketed && p5 instanceof E7 && ((l11 = W9.get(p5)) === null || l11 === void 0 ? void 0 : l11.overlay) === null && (d5 >= r2 || d5 + p5.length <= r2)) && !Ne6(n22, r2, d5, d5 + p5.length))) {
          if (p5 instanceof H8) {
            if (i9 & w9.ExcludeBuffers) continue;
            let m9 = p5.findChild(0, p5.buffer.length, t5, r2 - d5, n22);
            if (m9 > -1) return new G8(new fe8(f2, p5, e4, d5), null, m9);
          } else if (i9 & w9.IncludeAnonymous || !p5.type.isAnonymous || de9(p5)) {
            let m9;
            if (!(i9 & w9.IgnoreMounts) && (m9 = W9.get(p5)) && !m9.overlay) return new s94(m9.tree, d5, e4, f2);
            let x11 = new s94(p5, d5, e4, f2);
            return i9 & w9.IncludeAnonymous || !x11.type.isAnonymous ? x11 : x11.nextChild(t5 < 0 ? p5.children.length - 1 : 0, t5, r2, n22, i9);
          }
        }
      }
      if (i9 & w9.IncludeAnonymous || !f2.type.isAnonymous || (f2.index >= 0 ? e4 = f2.index + t5 : e4 = t5 < 0 ? -1 : f2._parent._tree.children.length, f2 = f2._parent, !f2)) return null;
    }
  }
  get firstChild() {
    return this.nextChild(0, 1, 0, 4);
  }
  get lastChild() {
    return this.nextChild(this._tree.children.length - 1, -1, 0, 4);
  }
  childAfter(e4) {
    return this.nextChild(0, 1, e4, 2);
  }
  childBefore(e4) {
    return this.nextChild(this._tree.children.length - 1, -1, e4, -2);
  }
  prop(e4) {
    return this._tree.prop(e4);
  }
  enter(e4, t5, r2 = 0) {
    let n22;
    if (!(r2 & w9.IgnoreOverlays) && (n22 = W9.get(this._tree)) && n22.overlay) {
      let i9 = e4 - this.from, l11 = r2 & w9.EnterBracketed && n22.bracketed;
      for (let { from: f2, to: h3 } of n22.overlay) if ((t5 > 0 || l11 ? f2 <= i9 : f2 < i9) && (t5 < 0 || l11 ? h3 >= i9 : h3 > i9)) return new s94(n22.tree, n22.overlay[0].from + this.from, -1, this);
    }
    return this.nextChild(0, 1, e4, t5, r2);
  }
  nextSignificantParent() {
    let e4 = this;
    for (; e4.type.isAnonymous && e4._parent; ) e4 = e4._parent;
    return e4;
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
  get tree() {
    return this._tree;
  }
  toTree() {
    return this._tree;
  }
  toString() {
    return this._tree.toString();
  }
};
function we7(s99, e4, t5, r2) {
  let n22 = s99.cursor(), i9 = [];
  if (!n22.firstChild()) return i9;
  if (t5 != null) {
    for (let l11 = false; !l11; ) if (l11 = n22.type.is(t5), !n22.nextSibling()) return i9;
  }
  for (; ; ) {
    if (r2 != null && n22.type.is(r2)) return i9;
    if (n22.type.is(e4) && i9.push(n22.node), !n22.nextSibling()) return r2 == null ? i9 : [];
  }
}
function le8(s99, e4, t5 = e4.length - 1) {
  for (let r2 = s99; t5 >= 0; r2 = r2.parent) {
    if (!r2) return false;
    if (!r2.type.isAnonymous) {
      if (e4[t5] && e4[t5] != r2.name) return false;
      t5--;
    }
  }
  return true;
}
var fe8 = class {
  constructor(e4, t5, r2, n22) {
    this.parent = e4, this.buffer = t5, this.index = r2, this.start = n22;
  }
};
var G8 = class s95 extends te9 {
  get name() {
    return this.type.name;
  }
  get from() {
    return this.context.start + this.context.buffer.buffer[this.index + 1];
  }
  get to() {
    return this.context.start + this.context.buffer.buffer[this.index + 2];
  }
  constructor(e4, t5, r2) {
    super(), this.context = e4, this._parent = t5, this.index = r2, this.type = e4.buffer.set.types[e4.buffer.buffer[r2]];
  }
  child(e4, t5, r2) {
    let { buffer: n22 } = this.context, i9 = n22.findChild(this.index + 4, n22.buffer[this.index + 3], e4, t5 - this.context.start, r2);
    return i9 < 0 ? null : new s95(this.context, this, i9);
  }
  get firstChild() {
    return this.child(1, 0, 4);
  }
  get lastChild() {
    return this.child(-1, 0, 4);
  }
  childAfter(e4) {
    return this.child(1, e4, 2);
  }
  childBefore(e4) {
    return this.child(-1, e4, -2);
  }
  prop(e4) {
    return this.type.prop(e4);
  }
  enter(e4, t5, r2 = 0) {
    if (r2 & w9.ExcludeBuffers) return null;
    let { buffer: n22 } = this.context, i9 = n22.findChild(this.index + 4, n22.buffer[this.index + 3], t5 > 0 ? 1 : -1, e4 - this.context.start, t5);
    return i9 < 0 ? null : new s95(this.context, this, i9);
  }
  get parent() {
    return this._parent || this.context.parent.nextSignificantParent();
  }
  externalSibling(e4) {
    return this._parent ? null : this.context.parent.nextChild(this.context.index + e4, e4, 0, 4);
  }
  get nextSibling() {
    let { buffer: e4 } = this.context, t5 = e4.buffer[this.index + 3];
    return t5 < (this._parent ? e4.buffer[this._parent.index + 3] : e4.buffer.length) ? new s95(this.context, this._parent, t5) : this.externalSibling(1);
  }
  get prevSibling() {
    let { buffer: e4 } = this.context, t5 = this._parent ? this._parent.index + 4 : 0;
    return this.index == t5 ? this.externalSibling(-1) : new s95(this.context, this._parent, e4.findChild(t5, this.index, -1, 0, 4));
  }
  get tree() {
    return null;
  }
  toTree() {
    let e4 = [], t5 = [], { buffer: r2 } = this.context, n22 = this.index + 4, i9 = r2.buffer[this.index + 3];
    if (i9 > n22) {
      let l11 = r2.buffer[this.index + 1];
      e4.push(r2.slice(n22, i9, l11)), t5.push(0);
    }
    return new E7(this.type, e4, t5, this.to - this.from);
  }
  toString() {
    return this.context.buffer.childString(this.index);
  }
};
function ze7(s99) {
  if (!s99.length) return null;
  let e4 = 0, t5 = s99[0];
  for (let i9 = 1; i9 < s99.length; i9++) {
    let l11 = s99[i9];
    (l11.from > t5.from || l11.to < t5.to) && (t5 = l11, e4 = i9);
  }
  let r2 = t5 instanceof P9 && t5.index < 0 ? null : t5.parent, n22 = s99.slice();
  return r2 ? n22[e4] = r2 : n22.splice(e4, 1), new he8(n22, t5);
}
var he8 = class {
  constructor(e4, t5) {
    this.heads = e4, this.node = t5;
  }
  get next() {
    return ze7(this.heads);
  }
};
function Ee7(s99, e4, t5) {
  let r2 = s99.resolveInner(e4, t5), n22 = null;
  for (let i9 = r2 instanceof P9 ? r2 : r2.context.parent; i9; i9 = i9.parent) if (i9.index < 0) {
    let l11 = i9.parent;
    (n22 || (n22 = [
      r2
    ])).push(l11.resolve(e4, t5)), i9 = l11;
  } else {
    let l11 = W9.get(i9.tree);
    if (l11 && l11.overlay && l11.overlay[0].from <= e4 && l11.overlay[l11.overlay.length - 1].to >= e4) {
      let f2 = new P9(l11.tree, l11.overlay[0].from + i9.from, -1, i9);
      (n22 || (n22 = [
        r2
      ])).push(Q10(f2, e4, t5, false));
    }
  }
  return n22 ? ze7(n22) : r2;
}
var q9 = class {
  get name() {
    return this.type.name;
  }
  constructor(e4, t5 = 0) {
    if (this.buffer = null, this.stack = [], this.index = 0, this.bufferNode = null, this.mode = t5 & ~w9.EnterBracketed, e4 instanceof P9) this.yieldNode(e4);
    else {
      this._tree = e4.context.parent, this.buffer = e4.context;
      for (let r2 = e4._parent; r2; r2 = r2._parent) this.stack.unshift(r2.index);
      this.bufferNode = e4, this.yieldBuf(e4.index);
    }
  }
  yieldNode(e4) {
    return e4 ? (this._tree = e4, this.type = e4.type, this.from = e4.from, this.to = e4.to, true) : false;
  }
  yieldBuf(e4, t5) {
    this.index = e4;
    let { start: r2, buffer: n22 } = this.buffer;
    return this.type = t5 || n22.set.types[n22.buffer[e4]], this.from = r2 + n22.buffer[e4 + 1], this.to = r2 + n22.buffer[e4 + 2], true;
  }
  yield(e4) {
    return e4 ? e4 instanceof P9 ? (this.buffer = null, this.yieldNode(e4)) : (this.buffer = e4.context, this.yieldBuf(e4.index, e4.type)) : false;
  }
  toString() {
    return this.buffer ? this.buffer.buffer.childString(this.index) : this._tree.toString();
  }
  enterChild(e4, t5, r2) {
    if (!this.buffer) return this.yield(this._tree.nextChild(e4 < 0 ? this._tree._tree.children.length - 1 : 0, e4, t5, r2, this.mode));
    let { buffer: n22 } = this.buffer, i9 = n22.findChild(this.index + 4, n22.buffer[this.index + 3], e4, t5 - this.buffer.start, r2);
    return i9 < 0 ? false : (this.stack.push(this.index), this.yieldBuf(i9));
  }
  firstChild() {
    return this.enterChild(1, 0, 4);
  }
  lastChild() {
    return this.enterChild(-1, 0, 4);
  }
  childAfter(e4) {
    return this.enterChild(1, e4, 2);
  }
  childBefore(e4) {
    return this.enterChild(-1, e4, -2);
  }
  enter(e4, t5, r2 = this.mode) {
    return this.buffer ? r2 & w9.ExcludeBuffers ? false : this.enterChild(1, e4, t5) : this.yield(this._tree.enter(e4, t5, r2));
  }
  parent() {
    if (!this.buffer) return this.yieldNode(this.mode & w9.IncludeAnonymous ? this._tree._parent : this._tree.parent);
    if (this.stack.length) return this.yieldBuf(this.stack.pop());
    let e4 = this.mode & w9.IncludeAnonymous ? this.buffer.parent : this.buffer.parent.nextSignificantParent();
    return this.buffer = null, this.yieldNode(e4);
  }
  sibling(e4) {
    if (!this.buffer) return this._tree._parent ? this.yield(this._tree.index < 0 ? null : this._tree._parent.nextChild(this._tree.index + e4, e4, 0, 4, this.mode)) : false;
    let { buffer: t5 } = this.buffer, r2 = this.stack.length - 1;
    if (e4 < 0) {
      let n22 = r2 < 0 ? 0 : this.stack[r2] + 4;
      if (this.index != n22) return this.yieldBuf(t5.findChild(n22, this.index, -1, 0, 4));
    } else {
      let n22 = t5.buffer[this.index + 3];
      if (n22 < (r2 < 0 ? t5.buffer.length : t5.buffer[this.stack[r2] + 3])) return this.yieldBuf(n22);
    }
    return r2 < 0 ? this.yield(this.buffer.parent.nextChild(this.buffer.index + e4, e4, 0, 4, this.mode)) : false;
  }
  nextSibling() {
    return this.sibling(1);
  }
  prevSibling() {
    return this.sibling(-1);
  }
  atLastNode(e4) {
    let t5, r2, { buffer: n22 } = this;
    if (n22) {
      if (e4 > 0) {
        if (this.index < n22.buffer.buffer.length) return false;
      } else for (let i9 = 0; i9 < this.index; i9++) if (n22.buffer.buffer[i9 + 3] < this.index) return false;
      ({ index: t5, parent: r2 } = n22);
    } else ({ index: t5, _parent: r2 } = this._tree);
    for (; r2; { index: t5, _parent: r2 } = r2) if (t5 > -1) for (let i9 = t5 + e4, l11 = e4 < 0 ? -1 : r2._tree.children.length; i9 != l11; i9 += e4) {
      let f2 = r2._tree.children[i9];
      if (this.mode & w9.IncludeAnonymous || f2 instanceof H8 || !f2.type.isAnonymous || de9(f2)) return false;
    }
    return true;
  }
  move(e4, t5) {
    if (t5 && this.enterChild(e4, 0, 4)) return true;
    for (; ; ) {
      if (this.sibling(e4)) return true;
      if (this.atLastNode(e4) || !this.parent()) return false;
    }
  }
  next(e4 = true) {
    return this.move(1, e4);
  }
  prev(e4 = true) {
    return this.move(-1, e4);
  }
  moveTo(e4, t5 = 0) {
    for (; (this.from == this.to || (t5 < 1 ? this.from >= e4 : this.from > e4) || (t5 > -1 ? this.to <= e4 : this.to < e4)) && this.parent(); ) ;
    for (; this.enterChild(1, e4, t5); ) ;
    return this;
  }
  get node() {
    if (!this.buffer) return this._tree;
    let e4 = this.bufferNode, t5 = null, r2 = 0;
    if (e4 && e4.context == this.buffer) e: for (let n22 = this.index, i9 = this.stack.length; i9 >= 0; ) {
      for (let l11 = e4; l11; l11 = l11._parent) if (l11.index == n22) {
        if (n22 == this.index) return l11;
        t5 = l11, r2 = i9 + 1;
        break e;
      }
      n22 = this.stack[--i9];
    }
    for (let n22 = r2; n22 < this.stack.length; n22++) t5 = new G8(this.buffer, t5, this.stack[n22]);
    return this.bufferNode = new G8(this.buffer, t5, this.index);
  }
  get tree() {
    return this.buffer ? null : this._tree._tree;
  }
  iterate(e4, t5) {
    for (let r2 = 0; ; ) {
      let n22 = false;
      if (this.type.isAnonymous || e4(this) !== false) {
        if (this.firstChild()) {
          r2++;
          continue;
        }
        this.type.isAnonymous || (n22 = true);
      }
      for (; ; ) {
        if (n22 && t5 && t5(this), n22 = this.type.isAnonymous, !r2) return;
        if (this.nextSibling()) break;
        this.parent(), r2--, n22 = true;
      }
    }
  }
  matchContext(e4) {
    if (!this.buffer) return le8(this.node.parent, e4);
    let { buffer: t5 } = this.buffer, { types: r2 } = t5.set;
    for (let n22 = e4.length - 1, i9 = this.stack.length - 1; n22 >= 0; i9--) {
      if (i9 < 0) return le8(this._tree, e4, n22);
      let l11 = r2[t5.buffer[this.stack[i9]]];
      if (!l11.isAnonymous) {
        if (e4[n22] && e4[n22] != l11.name) return false;
        n22--;
      }
    }
    return true;
  }
};
function de9(s99) {
  return s99.children.some((e4) => e4 instanceof H8 || !e4.type.isAnonymous || de9(e4));
}
function Oe7(s99) {
  var e4;
  let { buffer: t5, nodeSet: r2, maxBufferLength: n22 = 1024, reused: i9 = [], minRepeatType: l11 = r2.types.length } = s99, f2 = Array.isArray(t5) ? new se10(t5, t5.length) : t5, h3 = r2.types, o4 = 0, u5 = 0;
  function p5(b9, A11, a2, _11, y10, S11) {
    let { id: g6, start: c4, end: k13, size: C12 } = f2, N14 = u5, U14 = o4;
    if (C12 < 0) if (f2.next(), C12 == -1) {
      let L10 = i9[g6];
      a2.push(L10), _11.push(c4 - b9);
      return;
    } else if (C12 == -3) {
      o4 = g6;
      return;
    } else if (C12 == -4) {
      u5 = g6;
      return;
    } else throw new RangeError(`Unrecognized record size: ${C12}`);
    let K10 = h3[g6], X14, J8, me10 = c4 - b9;
    if (k13 - c4 <= n22 && (J8 = j12(f2.pos - A11, y10))) {
      let L10 = new Uint16Array(J8.size - J8.skip), T12 = f2.pos - J8.size, D9 = L10.length;
      for (; f2.pos > T12; ) D9 = F13(J8.start, L10, D9);
      X14 = new H8(L10, k13 - J8.start, r2), me10 = J8.start - b9;
    } else {
      let L10 = f2.pos - C12;
      f2.next();
      let T12 = [], D9 = [], V13 = g6 >= l11 ? g6 : -1, $9 = 0, Y11 = k13;
      for (; f2.pos > L10; ) V13 >= 0 && f2.id == V13 && f2.size >= 0 ? (f2.end <= Y11 - n22 && (x11(T12, D9, c4, $9, f2.end, Y11, V13, N14, U14), $9 = T12.length, Y11 = f2.end), f2.next()) : S11 > 2500 ? d5(c4, L10, T12, D9) : p5(c4, L10, T12, D9, V13, S11 + 1);
      if (V13 >= 0 && $9 > 0 && $9 < T12.length && x11(T12, D9, c4, $9, c4, Y11, V13, N14, U14), T12.reverse(), D9.reverse(), V13 > -1 && $9 > 0) {
        let be10 = m9(K10, U14);
        X14 = ge8(K10, T12, D9, 0, T12.length, 0, k13 - c4, be10, be10);
      } else X14 = z13(K10, T12, D9, k13 - c4, N14 - k13, U14);
    }
    a2.push(X14), _11.push(me10);
  }
  function d5(b9, A11, a2, _11) {
    let y10 = [], S11 = 0, g6 = -1;
    for (; f2.pos > A11; ) {
      let { id: c4, start: k13, end: C12, size: N14 } = f2;
      if (N14 > 4) f2.next();
      else {
        if (g6 > -1 && k13 < g6) break;
        g6 < 0 && (g6 = C12 - n22), y10.push(c4, k13, C12), S11++, f2.next();
      }
    }
    if (S11) {
      let c4 = new Uint16Array(S11 * 4), k13 = y10[y10.length - 2];
      for (let C12 = y10.length - 3, N14 = 0; C12 >= 0; C12 -= 3) c4[N14++] = y10[C12], c4[N14++] = y10[C12 + 1] - k13, c4[N14++] = y10[C12 + 2] - k13, c4[N14++] = N14;
      a2.push(new H8(c4, y10[2] - k13, r2)), _11.push(k13 - b9);
    }
  }
  function m9(b9, A11) {
    return (a2, _11, y10) => {
      let S11 = 0, g6 = a2.length - 1, c4, k13;
      if (g6 >= 0 && (c4 = a2[g6]) instanceof E7) {
        if (!g6 && c4.type == b9 && c4.length == y10) return c4;
        (k13 = c4.prop(v6.lookAhead)) && (S11 = _11[g6] + c4.length + k13);
      }
      return z13(b9, a2, _11, y10, S11, A11);
    };
  }
  function x11(b9, A11, a2, _11, y10, S11, g6, c4, k13) {
    let C12 = [], N14 = [];
    for (; b9.length > _11; ) C12.push(b9.pop()), N14.push(A11.pop() + a2 - y10);
    b9.push(z13(r2.types[g6], C12, N14, S11 - y10, c4 - S11, k13)), A11.push(y10 - a2);
  }
  function z13(b9, A11, a2, _11, y10, S11, g6) {
    if (S11) {
      let c4 = [
        v6.contextHash,
        S11
      ];
      g6 = g6 ? [
        c4
      ].concat(g6) : [
        c4
      ];
    }
    if (y10 > 25) {
      let c4 = [
        v6.lookAhead,
        y10
      ];
      g6 = g6 ? [
        c4
      ].concat(g6) : [
        c4
      ];
    }
    return new E7(b9, A11, a2, _11, g6);
  }
  function j12(b9, A11) {
    let a2 = f2.fork(), _11 = 0, y10 = 0, S11 = 0, g6 = a2.end - n22, c4 = {
      size: 0,
      start: 0,
      skip: 0
    };
    e: for (let k13 = a2.pos - b9; a2.pos > k13; ) {
      let C12 = a2.size;
      if (a2.id == A11 && C12 >= 0) {
        c4.size = _11, c4.start = y10, c4.skip = S11, S11 += 4, _11 += 4, a2.next();
        continue;
      }
      let N14 = a2.pos - C12;
      if (C12 < 0 || N14 < k13 || a2.start < g6) break;
      let U14 = a2.id >= l11 ? 4 : 0, K10 = a2.start;
      for (a2.next(); a2.pos > N14; ) {
        if (a2.size < 0) if (a2.size == -3 || a2.size == -4) U14 += 4;
        else break e;
        else a2.id >= l11 && (U14 += 4);
        a2.next();
      }
      y10 = K10, _11 += C12, S11 += U14;
    }
    return (A11 < 0 || _11 == b9) && (c4.size = _11, c4.start = y10, c4.skip = S11), c4.size > 4 ? c4 : void 0;
  }
  function F13(b9, A11, a2) {
    let { id: _11, start: y10, end: S11, size: g6 } = f2;
    if (f2.next(), g6 >= 0 && _11 < l11) {
      let c4 = a2;
      if (g6 > 4) {
        let k13 = f2.pos - (g6 - 4);
        for (; f2.pos > k13; ) a2 = F13(b9, A11, a2);
      }
      A11[--a2] = c4, A11[--a2] = S11 - b9, A11[--a2] = y10 - b9, A11[--a2] = _11;
    } else g6 == -3 ? o4 = _11 : g6 == -4 && (u5 = _11);
    return a2;
  }
  let O9 = [], B13 = [];
  for (; f2.pos > 0; ) p5(s99.start || 0, s99.bufferStart || 0, O9, B13, -1, 0);
  let R12 = (e4 = s99.length) !== null && e4 !== void 0 ? e4 : O9.length ? B13[0] + O9[0].length : 0;
  return new E7(h3[s99.topID], O9.reverse(), B13.reverse(), R12);
}
var ve8 = /* @__PURE__ */ new WeakMap();
function ee8(s99, e4) {
  if (!s99.isAnonymous || e4 instanceof H8 || e4.type != s99) return 1;
  let t5 = ve8.get(e4);
  if (t5 == null) {
    t5 = 1;
    for (let r2 of e4.children) {
      if (r2.type != s99 || !(r2 instanceof E7)) {
        t5 = 1;
        break;
      }
      t5 += ee8(s99, r2);
    }
    ve8.set(e4, t5);
  }
  return t5;
}
function ge8(s99, e4, t5, r2, n22, i9, l11, f2, h3) {
  let o4 = 0;
  for (let x11 = r2; x11 < n22; x11++) o4 += ee8(s99, e4[x11]);
  let u5 = Math.ceil(o4 * 1.5 / 8), p5 = [], d5 = [];
  function m9(x11, z13, j12, F13, O9) {
    for (let B13 = j12; B13 < F13; ) {
      let R12 = B13, b9 = z13[B13], A11 = ee8(s99, x11[B13]);
      for (B13++; B13 < F13; B13++) {
        let a2 = ee8(s99, x11[B13]);
        if (A11 + a2 >= u5) break;
        A11 += a2;
      }
      if (B13 == R12 + 1) {
        if (A11 > u5) {
          let a2 = x11[R12];
          m9(a2.children, a2.positions, 0, a2.children.length, z13[R12] + O9);
          continue;
        }
        p5.push(x11[R12]);
      } else {
        let a2 = z13[B13 - 1] + x11[B13 - 1].length - b9;
        p5.push(ge8(s99, x11, z13, R12, B13, b9, a2, null, h3));
      }
      d5.push(b9 + O9 - i9);
    }
  }
  return m9(e4, t5, r2, n22, 0), (f2 || h3)(p5, d5, l11);
}
var re8 = class s96 {
  constructor(e4, t5, r2, n22, i9 = false, l11 = false) {
    this.from = e4, this.to = t5, this.tree = r2, this.offset = n22, this.open = (i9 ? 1 : 0) | (l11 ? 2 : 0);
  }
  get openStart() {
    return (this.open & 1) > 0;
  }
  get openEnd() {
    return (this.open & 2) > 0;
  }
  static addTree(e4, t5 = [], r2 = false) {
    let n22 = [
      new s96(0, e4.length, e4, 0, false, r2)
    ];
    for (let i9 of t5) i9.to > e4.length && n22.push(i9);
    return n22;
  }
  static applyChanges(e4, t5, r2 = 128) {
    if (!t5.length) return e4;
    let n22 = [], i9 = 1, l11 = e4.length ? e4[0] : null;
    for (let f2 = 0, h3 = 0, o4 = 0; ; f2++) {
      let u5 = f2 < t5.length ? t5[f2] : null, p5 = u5 ? u5.fromA : 1e9;
      if (p5 - h3 >= r2) for (; l11 && l11.from < p5; ) {
        let d5 = l11;
        if (h3 >= d5.from || p5 <= d5.to || o4) {
          let m9 = Math.max(d5.from, h3) - o4, x11 = Math.min(d5.to, p5) - o4;
          d5 = m9 >= x11 ? null : new s96(m9, x11, d5.tree, d5.offset + o4, f2 > 0, !!u5);
        }
        if (d5 && n22.push(d5), l11.to > p5) break;
        l11 = i9 < e4.length ? e4[i9++] : null;
      }
      if (!u5) break;
      h3 = u5.toA, o4 = u5.toA - u5.toB;
    }
    return n22;
  }
};
var Ae7 = class {
  startParse(e4, t5, r2) {
    return typeof e4 == "string" && (e4 = new oe9(e4)), r2 = r2 ? r2.length ? r2.map((n22) => new I9(n22.from, n22.to)) : [
      new I9(0, 0)
    ] : [
      new I9(0, e4.length)
    ], this.createParse(e4, t5 || [], r2);
  }
  parse(e4, t5, r2) {
    let n22 = this.startParse(e4, t5, r2);
    for (; ; ) {
      let i9 = n22.advance();
      if (i9) return i9;
    }
  }
};
var oe9 = class {
  constructor(e4) {
    this.string = e4;
  }
  get length() {
    return this.string.length;
  }
  chunk(e4) {
    return this.string.slice(e4);
  }
  get lineChunks() {
    return false;
  }
  read(e4, t5) {
    return this.string.slice(e4, t5);
  }
};
var ae10 = new v6({
  perNode: true
});

// deno:https://esm.sh/@lezer/highlight@1.2.3/denonext/highlight.mjs
var G9 = 0;
var p4 = class s97 {
  constructor(t5, a2, n22, i9) {
    this.name = t5, this.set = a2, this.base = n22, this.modified = i9, this.id = G9++;
  }
  toString() {
    let { name: t5 } = this;
    for (let a2 of this.modified) a2.name && (t5 = `${a2.name}(${t5})`);
    return t5;
  }
  static define(t5, a2) {
    let n22 = typeof t5 == "string" ? t5 : "?";
    if (t5 instanceof s97 && (a2 = t5), a2?.base) throw new Error("Can not derive from a modified tag");
    let i9 = new s97(n22, [], null, []);
    if (i9.set.push(i9), a2) for (let o4 of a2.set) i9.set.push(o4);
    return i9;
  }
  static defineModifier(t5) {
    let a2 = new E8(t5);
    return (n22) => n22.modified.indexOf(a2) > -1 ? n22 : E8.get(n22.base || n22, n22.modified.concat(a2).sort((i9, o4) => i9.id - o4.id));
  }
};
var L8 = 0;
var E8 = class s98 {
  constructor(t5) {
    this.name = t5, this.instances = [], this.id = L8++;
  }
  static get(t5, a2) {
    if (!a2.length) return t5;
    let n22 = a2[0].instances.find((r2) => r2.base == t5 && P10(a2, r2.modified));
    if (n22) return n22;
    let i9 = [], o4 = new p4(t5.name, i9, t5, a2);
    for (let r2 of a2) r2.instances.push(o4);
    let h3 = Q11(a2);
    for (let r2 of t5.set) if (!r2.modified.length) for (let d5 of h3) i9.push(s98.get(r2, d5));
    return o4;
  }
};
function P10(s99, t5) {
  return s99.length == t5.length && s99.every((a2, n22) => a2 == t5[n22]);
}
function Q11(s99) {
  let t5 = [
    []
  ];
  for (let a2 = 0; a2 < s99.length; a2++) for (let n22 = 0, i9 = t5.length; n22 < i9; n22++) t5.push(t5[n22].concat(s99[a2]));
  return t5.sort((a2, n22) => n22.length - a2.length);
}
function _9(s99) {
  let t5 = /* @__PURE__ */ Object.create(null);
  for (let a2 in s99) {
    let n22 = s99[a2];
    Array.isArray(n22) || (n22 = [
      n22
    ]);
    for (let i9 of a2.split(" ")) if (i9) {
      let o4 = [], h3 = 2, r2 = i9;
      for (let g6 = 0; ; ) {
        if (r2 == "..." && g6 > 0 && g6 + 3 == i9.length) {
          h3 = 1;
          break;
        }
        let f2 = /^"(?:[^"\\]|\\.)*?"|[^\/!]+/.exec(r2);
        if (!f2) throw new RangeError("Invalid path: " + i9);
        if (o4.push(f2[0] == "*" ? "" : f2[0][0] == '"' ? JSON.parse(f2[0]) : f2[0]), g6 += f2[0].length, g6 == i9.length) break;
        let m9 = i9[g6++];
        if (g6 == i9.length && m9 == "!") {
          h3 = 0;
          break;
        }
        if (m9 != "/") throw new RangeError("Invalid path: " + i9);
        r2 = i9.slice(g6);
      }
      let d5 = o4.length - 1, c4 = o4[d5];
      if (!c4) throw new RangeError("Invalid path: " + i9);
      let x11 = new v7(n22, h3, d5 > 0 ? o4.slice(0, d5) : null);
      t5[c4] = x11.sort(t5[c4]);
    }
  }
  return z10.add(t5);
}
var z10 = new v6({
  combine(s99, t5) {
    let a2, n22, i9;
    for (; s99 || t5; ) {
      if (!s99 || t5 && s99.depth >= t5.depth ? (i9 = t5, t5 = t5.next) : (i9 = s99, s99 = s99.next), a2 && a2.mode == i9.mode && !i9.context && !a2.context) continue;
      let o4 = new v7(i9.tags, i9.mode, i9.context);
      a2 ? a2.next = o4 : n22 = o4, a2 = o4;
    }
    return n22;
  }
});
var v7 = class {
  constructor(t5, a2, n22, i9) {
    this.tags = t5, this.mode = a2, this.context = n22, this.next = i9;
  }
  get opaque() {
    return this.mode == 0;
  }
  get inherit() {
    return this.mode == 1;
  }
  sort(t5) {
    return !t5 || t5.depth < this.depth ? (this.next = t5, this) : (t5.next = this.sort(t5.next), t5);
  }
  get depth() {
    return this.context ? this.context.length : 0;
  }
};
v7.empty = new v7([], 2, null);
function U10(s99, t5) {
  let a2 = /* @__PURE__ */ Object.create(null);
  for (let o4 of s99) if (!Array.isArray(o4.tag)) a2[o4.tag.id] = o4.class;
  else for (let h3 of o4.tag) a2[h3.id] = o4.class;
  let { scope: n22, all: i9 = null } = t5 || {};
  return {
    style: (o4) => {
      let h3 = i9;
      for (let r2 of o4) for (let d5 of r2.set) {
        let c4 = a2[d5.id];
        if (c4) {
          h3 = h3 ? h3 + " " + c4 : c4;
          break;
        }
      }
      return h3;
    },
    scope: n22
  };
}
function W10(s99, t5) {
  let a2 = null;
  for (let n22 of s99) {
    let i9 = n22.style(t5);
    i9 && (a2 = a2 ? a2 + " " + i9 : i9);
  }
  return a2;
}
function X10(s99, t5, a2, n22 = 0, i9 = s99.length) {
  let o4 = new B10(n22, Array.isArray(t5) ? t5 : [
    t5
  ], a2);
  o4.highlightRange(s99.cursor(), n22, i9, "", o4.highlighters), o4.flush(i9);
}
var B10 = class {
  constructor(t5, a2, n22) {
    this.at = t5, this.highlighters = a2, this.span = n22, this.class = "";
  }
  startSpan(t5, a2) {
    a2 != this.class && (this.flush(t5), t5 > this.at && (this.at = t5), this.class = a2);
  }
  flush(t5) {
    t5 > this.at && this.class && this.span(this.at, t5, this.class);
  }
  highlightRange(t5, a2, n22, i9, o4) {
    let { type: h3, from: r2, to: d5 } = t5;
    if (r2 >= n22 || d5 <= a2) return;
    h3.isTop && (o4 = this.highlighters.filter((m9) => !m9.scope || m9.scope(h3)));
    let c4 = i9, x11 = Y8(t5) || v7.empty, g6 = W10(o4, x11.tags);
    if (g6 && (c4 && (c4 += " "), c4 += g6, x11.mode == 1 && (i9 += (i9 ? " " : "") + g6)), this.startSpan(Math.max(a2, r2), c4), x11.opaque) return;
    let f2 = t5.tree && t5.tree.prop(v6.mounted);
    if (f2 && f2.overlay) {
      let m9 = t5.node.enter(f2.overlay[0].from + r2, 1), R12 = this.highlighters.filter((M14) => !M14.scope || M14.scope(f2.tree.type)), H10 = t5.firstChild();
      for (let M14 = 0, S11 = r2; ; M14++) {
        let O9 = M14 < f2.overlay.length ? f2.overlay[M14] : null, K10 = O9 ? O9.from + r2 : d5, $9 = Math.max(a2, S11), T12 = Math.min(n22, K10);
        if ($9 < T12 && H10) for (; t5.from < T12 && (this.highlightRange(t5, $9, T12, i9, o4), this.startSpan(Math.min(T12, t5.to), c4), !(t5.to >= K10 || !t5.nextSibling())); ) ;
        if (!O9 || K10 > n22) break;
        S11 = O9.to + r2, S11 > a2 && (this.highlightRange(m9.cursor(), Math.max(a2, O9.from + r2), Math.min(n22, S11), "", R12), this.startSpan(Math.min(n22, S11), c4));
      }
      H10 && t5.parent();
    } else if (t5.firstChild()) {
      f2 && (i9 = "");
      do
        if (!(t5.to <= a2)) {
          if (t5.from >= n22) break;
          this.highlightRange(t5, a2, n22, i9, o4), this.startSpan(Math.min(n22, t5.to), c4);
        }
      while (t5.nextSibling());
      t5.parent();
    }
  }
};
function Y8(s99) {
  let t5 = s99.type.prop(z10);
  for (; t5 && t5.context && !s99.matchContext(t5.context); ) t5 = t5.next;
  return t5 || null;
}
var e3 = p4.define;
var C9 = e3();
var b8 = e3();
var F9 = e3(b8);
var J7 = e3(b8);
var N11 = e3();
var I10 = e3(N11);
var j9 = e3(N11);
var y9 = e3();
var w10 = e3(y9);
var u4 = e3();
var k9 = e3();
var D8 = e3();
var A9 = e3(D8);
var q10 = e3();
var l10 = {
  comment: C9,
  lineComment: e3(C9),
  blockComment: e3(C9),
  docComment: e3(C9),
  name: b8,
  variableName: e3(b8),
  typeName: F9,
  tagName: e3(F9),
  propertyName: J7,
  attributeName: e3(J7),
  className: e3(b8),
  labelName: e3(b8),
  namespace: e3(b8),
  macroName: e3(b8),
  literal: N11,
  string: I10,
  docString: e3(I10),
  character: e3(I10),
  attributeValue: e3(I10),
  number: j9,
  integer: e3(j9),
  float: e3(j9),
  bool: e3(N11),
  regexp: e3(N11),
  escape: e3(N11),
  color: e3(N11),
  url: e3(N11),
  keyword: u4,
  self: e3(u4),
  null: e3(u4),
  atom: e3(u4),
  unit: e3(u4),
  modifier: e3(u4),
  operatorKeyword: e3(u4),
  controlKeyword: e3(u4),
  definitionKeyword: e3(u4),
  moduleKeyword: e3(u4),
  operator: k9,
  derefOperator: e3(k9),
  arithmeticOperator: e3(k9),
  logicOperator: e3(k9),
  bitwiseOperator: e3(k9),
  compareOperator: e3(k9),
  updateOperator: e3(k9),
  definitionOperator: e3(k9),
  typeOperator: e3(k9),
  controlOperator: e3(k9),
  punctuation: D8,
  separator: e3(D8),
  bracket: A9,
  angleBracket: e3(A9),
  squareBracket: e3(A9),
  paren: e3(A9),
  brace: e3(A9),
  content: y9,
  heading: w10,
  heading1: e3(w10),
  heading2: e3(w10),
  heading3: e3(w10),
  heading4: e3(w10),
  heading5: e3(w10),
  heading6: e3(w10),
  contentSeparator: e3(y9),
  list: e3(y9),
  quote: e3(y9),
  emphasis: e3(y9),
  strong: e3(y9),
  link: e3(y9),
  monospace: e3(y9),
  strikethrough: e3(y9),
  inserted: e3(),
  deleted: e3(),
  changed: e3(),
  invalid: e3(),
  meta: q10,
  documentMeta: e3(q10),
  annotation: e3(q10),
  processingInstruction: e3(q10),
  definition: p4.defineModifier("definition"),
  constant: p4.defineModifier("constant"),
  function: p4.defineModifier("function"),
  standard: p4.defineModifier("standard"),
  local: p4.defineModifier("local"),
  special: p4.defineModifier("special")
};
for (let s99 in l10) {
  let t5 = l10[s99];
  t5 instanceof p4 && (t5.name = s99);
}
var et5 = U10([
  {
    tag: l10.link,
    class: "tok-link"
  },
  {
    tag: l10.heading,
    class: "tok-heading"
  },
  {
    tag: l10.emphasis,
    class: "tok-emphasis"
  },
  {
    tag: l10.strong,
    class: "tok-strong"
  },
  {
    tag: l10.keyword,
    class: "tok-keyword"
  },
  {
    tag: l10.atom,
    class: "tok-atom"
  },
  {
    tag: l10.bool,
    class: "tok-bool"
  },
  {
    tag: l10.url,
    class: "tok-url"
  },
  {
    tag: l10.labelName,
    class: "tok-labelName"
  },
  {
    tag: l10.inserted,
    class: "tok-inserted"
  },
  {
    tag: l10.deleted,
    class: "tok-deleted"
  },
  {
    tag: l10.literal,
    class: "tok-literal"
  },
  {
    tag: l10.string,
    class: "tok-string"
  },
  {
    tag: l10.number,
    class: "tok-number"
  },
  {
    tag: [
      l10.regexp,
      l10.escape,
      l10.special(l10.string)
    ],
    class: "tok-string2"
  },
  {
    tag: l10.variableName,
    class: "tok-variableName"
  },
  {
    tag: l10.local(l10.variableName),
    class: "tok-variableName tok-local"
  },
  {
    tag: l10.definition(l10.variableName),
    class: "tok-variableName tok-definition"
  },
  {
    tag: l10.special(l10.variableName),
    class: "tok-variableName2"
  },
  {
    tag: l10.definition(l10.propertyName),
    class: "tok-propertyName tok-definition"
  },
  {
    tag: l10.typeName,
    class: "tok-typeName"
  },
  {
    tag: l10.namespace,
    class: "tok-namespace"
  },
  {
    tag: l10.className,
    class: "tok-className"
  },
  {
    tag: l10.macroName,
    class: "tok-macroName"
  },
  {
    tag: l10.propertyName,
    class: "tok-propertyName"
  },
  {
    tag: l10.operator,
    class: "tok-operator"
  },
  {
    tag: l10.comment,
    class: "tok-comment"
  },
  {
    tag: l10.meta,
    class: "tok-meta"
  },
  {
    tag: l10.invalid,
    class: "tok-invalid"
  },
  {
    tag: l10.punctuation,
    class: "tok-punctuation"
  }
]);

// deno:https://esm.sh/@codemirror/language@6.11.0/denonext/language.mjs
var X11;
var S8 = new v6();
function Lt6(n22) {
  return k7.define({
    combine: n22 ? (t5) => t5.concat(n22) : void 0
  });
}
var ce11 = new v6();
var d3 = class {
  constructor(t5, e4, r2 = [], i9 = "") {
    this.data = t5, this.name = i9, P7.prototype.hasOwnProperty("tree") || Object.defineProperty(P7.prototype, "tree", {
      get() {
        return k10(this);
      }
    }), this.parser = e4, this.extension = [
      x9.of(this),
      P7.languageData.of((s99, o4, a2) => {
        let l11 = kt5(s99, o4, a2), f2 = l11.type.prop(S8);
        if (!f2) return [];
        let h3 = s99.facet(f2), c4 = l11.type.prop(ce11);
        if (c4) {
          let w11 = l11.resolve(o4 - l11.from, a2);
          for (let b9 of c4) if (b9.test(w11, s99)) {
            let P12 = s99.facet(b9.facet);
            return b9.type == "replace" ? P12 : P12.concat(h3);
          }
        }
        return h3;
      })
    ].concat(r2);
  }
  isActiveAt(t5, e4, r2 = -1) {
    return kt5(t5, e4, r2).type.prop(S8) == this.data;
  }
  findRegions(t5) {
    let e4 = t5.facet(x9);
    if (e4?.data == this.data) return [
      {
        from: 0,
        to: t5.doc.length
      }
    ];
    if (!e4 || !e4.allowsNesting) return [];
    let r2 = [], i9 = (s99, o4) => {
      if (s99.prop(S8) == this.data) {
        r2.push({
          from: o4,
          to: o4 + s99.length
        });
        return;
      }
      let a2 = s99.prop(v6.mounted);
      if (a2) {
        if (a2.tree.prop(S8) == this.data) {
          if (a2.overlay) for (let l11 of a2.overlay) r2.push({
            from: l11.from + o4,
            to: l11.to + o4
          });
          else r2.push({
            from: o4,
            to: o4 + s99.length
          });
          return;
        } else if (a2.overlay) {
          let l11 = r2.length;
          if (i9(a2.tree, a2.overlay[0].from + o4), r2.length > l11) return;
        }
      }
      for (let l11 = 0; l11 < s99.children.length; l11++) {
        let f2 = s99.children[l11];
        f2 instanceof E7 && i9(f2, s99.positions[l11] + o4);
      }
    };
    return i9(k10(t5), 0), r2;
  }
  get allowsNesting() {
    return true;
  }
};
d3.setState = v5.define();
function kt5(n22, t5, e4) {
  let r2 = n22.facet(x9), i9 = k10(n22).topNode;
  if (!r2 || r2.allowsNesting) for (let s99 = i9; s99; s99 = s99.enter(t5, e4, w9.ExcludeBuffers)) s99.type.isTop && (i9 = s99);
  return i9;
}
var bt5 = class n12 extends d3 {
  constructor(t5, e4, r2) {
    super(t5, e4, [], r2), this.parser = e4;
  }
  static define(t5) {
    let e4 = Lt6(t5.languageData);
    return new n12(e4, t5.parser.configure({
      props: [
        S8.add((r2) => r2.isTop ? e4 : void 0)
      ]
    }), t5.name);
  }
  configure(t5, e4) {
    return new n12(this.data, this.parser.configure(t5), e4 || this.name);
  }
  get allowsNesting() {
    return this.parser.hasWrappers();
  }
};
function k10(n22) {
  let t5 = n22.field(d3.state, false);
  return t5 ? t5.tree : E7.empty;
}
function de10(n22, t5, e4 = 50) {
  var r2;
  let i9 = (r2 = n22.field(d3.state, false)) === null || r2 === void 0 ? void 0 : r2.context;
  if (!i9) return null;
  let s99 = i9.viewport;
  i9.updateViewport({
    from: 0,
    to: t5
  });
  let o4 = i9.isDone(t5) || i9.work(e4, t5) ? i9.tree : null;
  return i9.updateViewport(s99), o4;
}
function ln4(n22, t5 = n22.doc.length) {
  var e4;
  return ((e4 = n22.field(d3.state, false)) === null || e4 === void 0 ? void 0 : e4.context.isDone(t5)) || false;
}
function an4(n22, t5 = n22.viewport.to, e4 = 100) {
  let r2 = de10(n22.state, t5, e4);
  return r2 != k10(n22.state) && n22.dispatch({}), !!r2;
}
function fn2(n22) {
  var t5;
  return ((t5 = n22.plugin(Et5)) === null || t5 === void 0 ? void 0 : t5.isWorking()) || false;
}
var tt7 = class {
  constructor(t5) {
    this.doc = t5, this.cursorPos = 0, this.string = "", this.cursor = t5.iter();
  }
  get length() {
    return this.doc.length;
  }
  syncTo(t5) {
    return this.string = this.cursor.next(t5 - this.cursorPos).value, this.cursorPos = t5 + this.string.length, this.cursorPos - this.string.length;
  }
  chunk(t5) {
    return this.syncTo(t5), this.string;
  }
  get lineChunks() {
    return true;
  }
  read(t5, e4) {
    let r2 = this.cursorPos - this.string.length;
    return t5 < r2 || e4 >= this.cursorPos ? this.doc.sliceString(t5, e4) : this.string.slice(t5 - r2, e4 - r2);
  }
};
var I11 = null;
var M11 = class n13 {
  constructor(t5, e4, r2 = [], i9, s99, o4, a2, l11) {
    this.parser = t5, this.state = e4, this.fragments = r2, this.tree = i9, this.treeLen = s99, this.viewport = o4, this.skipped = a2, this.scheduleOn = l11, this.parse = null, this.tempSkipped = [];
  }
  static create(t5, e4, r2) {
    return new n13(t5, e4, [], E7.empty, 0, r2, [], null);
  }
  startParse() {
    return this.parser.startParse(new tt7(this.state.doc), this.fragments);
  }
  work(t5, e4) {
    return e4 != null && e4 >= this.state.doc.length && (e4 = void 0), this.tree != E7.empty && this.isDone(e4 ?? this.state.doc.length) ? (this.takeTree(), true) : this.withContext(() => {
      var r2;
      if (typeof t5 == "number") {
        let i9 = Date.now() + t5;
        t5 = () => Date.now() > i9;
      }
      for (this.parse || (this.parse = this.startParse()), e4 != null && (this.parse.stoppedAt == null || this.parse.stoppedAt > e4) && e4 < this.state.doc.length && this.parse.stopAt(e4); ; ) {
        let i9 = this.parse.advance();
        if (i9) if (this.fragments = this.withoutTempSkipped(re8.addTree(i9, this.fragments, this.parse.stoppedAt != null)), this.treeLen = (r2 = this.parse.stoppedAt) !== null && r2 !== void 0 ? r2 : this.state.doc.length, this.tree = i9, this.parse = null, this.treeLen < (e4 ?? this.state.doc.length)) this.parse = this.startParse();
        else return true;
        if (t5()) return false;
      }
    });
  }
  takeTree() {
    let t5, e4;
    this.parse && (t5 = this.parse.parsedPos) >= this.treeLen && ((this.parse.stoppedAt == null || this.parse.stoppedAt > t5) && this.parse.stopAt(t5), this.withContext(() => {
      for (; !(e4 = this.parse.advance()); ) ;
    }), this.treeLen = t5, this.tree = e4, this.fragments = this.withoutTempSkipped(re8.addTree(this.tree, this.fragments, true)), this.parse = null);
  }
  withContext(t5) {
    let e4 = I11;
    I11 = this;
    try {
      return t5();
    } finally {
      I11 = e4;
    }
  }
  withoutTempSkipped(t5) {
    for (let e4; e4 = this.tempSkipped.pop(); ) t5 = wt5(t5, e4.from, e4.to);
    return t5;
  }
  changes(t5, e4) {
    let { fragments: r2, tree: i9, treeLen: s99, viewport: o4, skipped: a2 } = this;
    if (this.takeTree(), !t5.empty) {
      let l11 = [];
      if (t5.iterChangedRanges((f2, h3, c4, w11) => l11.push({
        fromA: f2,
        toA: h3,
        fromB: c4,
        toB: w11
      })), r2 = re8.applyChanges(r2, l11), i9 = E7.empty, s99 = 0, o4 = {
        from: t5.mapPos(o4.from, -1),
        to: t5.mapPos(o4.to, 1)
      }, this.skipped.length) {
        a2 = [];
        for (let f2 of this.skipped) {
          let h3 = t5.mapPos(f2.from, 1), c4 = t5.mapPos(f2.to, -1);
          h3 < c4 && a2.push({
            from: h3,
            to: c4
          });
        }
      }
    }
    return new n13(this.parser, e4, r2, i9, s99, o4, a2, this.scheduleOn);
  }
  updateViewport(t5) {
    if (this.viewport.from == t5.from && this.viewport.to == t5.to) return false;
    this.viewport = t5;
    let e4 = this.skipped.length;
    for (let r2 = 0; r2 < this.skipped.length; r2++) {
      let { from: i9, to: s99 } = this.skipped[r2];
      i9 < t5.to && s99 > t5.from && (this.fragments = wt5(this.fragments, i9, s99), this.skipped.splice(r2--, 1));
    }
    return this.skipped.length >= e4 ? false : (this.reset(), true);
  }
  reset() {
    this.parse && (this.takeTree(), this.parse = null);
  }
  skipUntilInView(t5, e4) {
    this.skipped.push({
      from: t5,
      to: e4
    });
  }
  static getSkippingParser(t5) {
    return new class extends Ae7 {
      createParse(e4, r2, i9) {
        let s99 = i9[0].from, o4 = i9[i9.length - 1].to;
        return {
          parsedPos: s99,
          advance() {
            let l11 = I11;
            if (l11) {
              for (let f2 of i9) l11.tempSkipped.push(f2);
              t5 && (l11.scheduleOn = l11.scheduleOn ? Promise.all([
                l11.scheduleOn,
                t5
              ]) : t5);
            }
            return this.parsedPos = o4, new E7(M10.none, [], [], o4 - s99);
          },
          stoppedAt: null,
          stopAt() {
          }
        };
      }
    }();
  }
  isDone(t5) {
    t5 = Math.min(t5, this.state.doc.length);
    let e4 = this.fragments;
    return this.treeLen >= t5 && e4.length && e4[0].from == 0 && e4[0].to >= t5;
  }
  static get() {
    return I11;
  }
};
function wt5(n22, t5, e4) {
  return re8.applyChanges(n22, [
    {
      fromA: t5,
      toA: e4,
      fromB: t5,
      toB: e4
    }
  ]);
}
var B11 = class n14 {
  constructor(t5) {
    this.context = t5, this.tree = t5.tree;
  }
  apply(t5) {
    if (!t5.docChanged && this.tree == this.context.tree) return this;
    let e4 = this.context.changes(t5.changes, t5.state), r2 = this.context.treeLen == t5.startState.doc.length ? void 0 : Math.max(t5.changes.mapPos(this.context.treeLen), e4.viewport.to);
    return e4.work(20, r2) || e4.takeTree(), new n14(e4);
  }
  static init(t5) {
    let e4 = Math.min(3e3, t5.doc.length), r2 = M11.create(t5.facet(x9).parser, t5, {
      from: 0,
      to: e4
    });
    return r2.work(20, e4) || r2.takeTree(), new n14(r2);
  }
};
d3.state = z8.define({
  create: B11.init,
  update(n22, t5) {
    for (let e4 of t5.effects) if (e4.is(d3.setState)) return e4.value;
    return t5.startState.facet(x9) != t5.state.facet(x9) ? B11.init(t5.state) : n22.apply(t5);
  }
});
var Rt5 = (n22) => {
  let t5 = setTimeout(() => n22(), 500);
  return () => clearTimeout(t5);
};
typeof requestIdleCallback < "u" && (Rt5 = (n22) => {
  let t5 = -1, e4 = setTimeout(() => {
    t5 = requestIdleCallback(n22, {
      timeout: 400
    });
  }, 100);
  return () => t5 < 0 ? clearTimeout(e4) : cancelIdleCallback(t5);
});
var Y9 = typeof navigator < "u" && (!((X11 = navigator.scheduling) === null || X11 === void 0) && X11.isInputPending) ? () => navigator.scheduling.isInputPending() : null;
var Et5 = N10.fromClass(class {
  constructor(t5) {
    this.view = t5, this.working = null, this.workScheduled = 0, this.chunkEnd = -1, this.chunkBudget = -1, this.work = this.work.bind(this), this.scheduleWork();
  }
  update(t5) {
    let e4 = this.view.state.field(d3.state).context;
    (e4.updateViewport(t5.view.viewport) || this.view.viewport.to > e4.treeLen) && this.scheduleWork(), (t5.docChanged || t5.selectionSet) && (this.view.hasFocus && (this.chunkBudget += 50), this.scheduleWork()), this.checkAsyncSchedule(e4);
  }
  scheduleWork() {
    if (this.working) return;
    let { state: t5 } = this.view, e4 = t5.field(d3.state);
    (e4.tree != e4.context.tree || !e4.context.isDone(t5.doc.length)) && (this.working = Rt5(this.work));
  }
  work(t5) {
    this.working = null;
    let e4 = Date.now();
    if (this.chunkEnd < e4 && (this.chunkEnd < 0 || this.view.hasFocus) && (this.chunkEnd = e4 + 3e4, this.chunkBudget = 3e3), this.chunkBudget <= 0) return;
    let { state: r2, viewport: { to: i9 } } = this.view, s99 = r2.field(d3.state);
    if (s99.tree == s99.context.tree && s99.context.isDone(i9 + 1e5)) return;
    let o4 = Date.now() + Math.min(this.chunkBudget, 100, t5 && !Y9 ? Math.max(25, t5.timeRemaining() - 5) : 1e9), a2 = s99.context.treeLen < i9 && r2.doc.length > i9 + 1e3, l11 = s99.context.work(() => Y9 && Y9() || Date.now() > o4, i9 + (a2 ? 0 : 1e5));
    this.chunkBudget -= Date.now() - e4, (l11 || this.chunkBudget <= 0) && (s99.context.takeTree(), this.view.dispatch({
      effects: d3.setState.of(new B11(s99.context))
    })), this.chunkBudget > 0 && !(l11 && !a2) && this.scheduleWork(), this.checkAsyncSchedule(s99.context);
  }
  checkAsyncSchedule(t5) {
    t5.scheduleOn && (this.workScheduled++, t5.scheduleOn.then(() => this.scheduleWork()).catch((e4) => U9(this.view.state, e4)).then(() => this.workScheduled--), t5.scheduleOn = null);
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
var x9 = k7.define({
  combine(n22) {
    return n22.length ? n22[0] : null;
  },
  enables: (n22) => [
    d3.state,
    Et5,
    k8.contentAttributes.compute([
      n22
    ], (t5) => {
      let e4 = t5.facet(n22);
      return e4 && e4.name ? {
        "data-language": e4.name
      } : {};
    })
  ]
});
var yt5 = class {
  constructor(t5, e4 = []) {
    this.language = t5, this.support = e4, this.extension = [
      t5,
      e4
    ];
  }
};
var vt4 = class n15 {
  constructor(t5, e4, r2, i9, s99, o4 = void 0) {
    this.name = t5, this.alias = e4, this.extensions = r2, this.filename = i9, this.loadFunc = s99, this.support = o4, this.loading = null;
  }
  load() {
    return this.loading || (this.loading = this.loadFunc().then((t5) => this.support = t5, (t5) => {
      throw this.loading = null, t5;
    }));
  }
  static of(t5) {
    let { load: e4, support: r2 } = t5;
    if (!e4) {
      if (!r2) throw new RangeError("Must pass either 'load' or 'support' to LanguageDescription.of");
      e4 = () => Promise.resolve(r2);
    }
    return new n15(t5.name, (t5.alias || []).concat(t5.name).map((i9) => i9.toLowerCase()), t5.extensions || [], t5.filename, e4, r2);
  }
  static matchFilename(t5, e4) {
    for (let i9 of t5) if (i9.filename && i9.filename.test(e4)) return i9;
    let r2 = /\.([^.]+)$/.exec(e4);
    if (r2) {
      for (let i9 of t5) if (i9.extensions.indexOf(r2[1]) > -1) return i9;
    }
    return null;
  }
  static matchLanguageName(t5, e4, r2 = true) {
    e4 = e4.toLowerCase();
    for (let i9 of t5) if (i9.alias.some((s99) => s99 == e4)) return i9;
    if (r2) for (let i9 of t5) for (let s99 of i9.alias) {
      let o4 = e4.indexOf(s99);
      if (o4 > -1 && (s99.length > 2 || !/\w/.test(e4[o4 - 1]) && !/\w/.test(e4[o4 + s99.length]))) return i9;
    }
    return null;
  }
};
var pe8 = k7.define();
var Ft4 = k7.define({
  combine: (n22) => {
    if (!n22.length) return "  ";
    let t5 = n22[0];
    if (!t5 || /\S/.test(t5) || Array.from(t5).some((e4) => e4 != t5[0])) throw new Error("Invalid indent unit: " + JSON.stringify(n22[0]));
    return t5;
  }
});
function V11(n22) {
  let t5 = n22.facet(Ft4);
  return t5.charCodeAt(0) == 9 ? n22.tabSize * t5.length : t5.length;
}
function Ut5(n22, t5) {
  let e4 = "", r2 = n22.tabSize, i9 = n22.facet(Ft4)[0];
  if (i9 == "	") {
    for (; t5 >= r2; ) e4 += "	", t5 -= r2;
    i9 = " ";
  }
  for (let s99 = 0; s99 < t5; s99++) e4 += i9;
  return e4;
}
function Wt4(n22, t5) {
  n22 instanceof P7 && (n22 = new N12(n22));
  for (let r2 of n22.state.facet(pe8)) {
    let i9 = r2(n22, t5);
    if (i9 !== void 0) return i9;
  }
  let e4 = k10(n22.state);
  return e4.length >= t5 ? me7(n22, e4, t5) : null;
}
function un3(n22, t5, e4) {
  let r2 = /* @__PURE__ */ Object.create(null), i9 = new N12(n22, {
    overrideIndentation: (o4) => {
      var a2;
      return (a2 = r2[o4]) !== null && a2 !== void 0 ? a2 : -1;
    }
  }), s99 = [];
  for (let o4 = t5; o4 <= e4; ) {
    let a2 = n22.doc.lineAt(o4);
    o4 = a2.to + 1;
    let l11 = Wt4(i9, a2.from);
    if (l11 == null) continue;
    /\S/.test(a2.text) || (l11 = 0);
    let f2 = /^\s*/.exec(a2.text)[0], h3 = Ut5(n22, l11);
    f2 != h3 && (r2[a2.from] = l11, s99.push({
      from: a2.from,
      to: a2.from + f2.length,
      insert: h3
    }));
  }
  return n22.changes(s99);
}
var N12 = class {
  constructor(t5, e4 = {}) {
    this.state = t5, this.options = e4, this.unit = V11(t5);
  }
  lineAt(t5, e4 = 1) {
    let r2 = this.state.doc.lineAt(t5), { simulateBreak: i9, simulateDoubleBreak: s99 } = this.options;
    return i9 != null && i9 >= r2.from && i9 <= r2.to ? s99 && i9 == t5 ? {
      text: "",
      from: t5
    } : (e4 < 0 ? i9 < t5 : i9 <= t5) ? {
      text: r2.text.slice(i9 - r2.from),
      from: i9
    } : {
      text: r2.text.slice(0, i9 - r2.from),
      from: r2.from
    } : r2;
  }
  textAfterPos(t5, e4 = 1) {
    if (this.options.simulateDoubleBreak && t5 == this.options.simulateBreak) return "";
    let { text: r2, from: i9 } = this.lineAt(t5, e4);
    return r2.slice(t5 - i9, Math.min(r2.length, t5 + 100 - i9));
  }
  column(t5, e4 = 1) {
    let { text: r2, from: i9 } = this.lineAt(t5, e4), s99 = this.countColumn(r2, t5 - i9), o4 = this.options.overrideIndentation ? this.options.overrideIndentation(i9) : -1;
    return o4 > -1 && (s99 += o4 - this.countColumn(r2, r2.search(/\S|$/))), s99;
  }
  countColumn(t5, e4 = t5.length) {
    return lt4(t5, this.state.tabSize, e4);
  }
  lineIndent(t5, e4 = 1) {
    let { text: r2, from: i9 } = this.lineAt(t5, e4), s99 = this.options.overrideIndentation;
    if (s99) {
      let o4 = s99(i9);
      if (o4 > -1) return o4;
    }
    return this.countColumn(r2, r2.search(/\S|$/));
  }
  get simulatedBreak() {
    return this.options.simulateBreak || null;
  }
};
var jt6 = new v6();
function me7(n22, t5, e4) {
  let r2 = t5.resolveStack(e4), i9 = t5.resolveInner(e4, -1).resolve(e4, 0).enterUnfinishedNodesBefore(e4);
  if (i9 != r2.node) {
    let s99 = [];
    for (let o4 = i9; o4 && !(o4.from == r2.node.from && o4.type == r2.node.type); o4 = o4.parent) s99.push(o4);
    for (let o4 = s99.length - 1; o4 >= 0; o4--) r2 = {
      node: s99[o4],
      next: r2
    };
  }
  return Ht5(r2, n22, e4);
}
function Ht5(n22, t5, e4) {
  for (let r2 = n22; r2; r2 = r2.next) {
    let i9 = ke9(r2.node);
    if (i9) return i9(et6.create(t5, e4, r2));
  }
  return 0;
}
function ge9(n22) {
  return n22.pos == n22.options.simulateBreak && n22.options.simulateDoubleBreak;
}
function ke9(n22) {
  let t5 = n22.type.prop(jt6);
  if (t5) return t5;
  let e4 = n22.firstChild, r2;
  if (e4 && (r2 = e4.type.prop(v6.closedBy))) {
    let i9 = n22.lastChild, s99 = i9 && r2.indexOf(i9.name) > -1;
    return (o4) => Vt3(o4, true, 1, void 0, s99 && !ge9(o4) ? i9.from : void 0);
  }
  return n22.parent == null ? be8 : null;
}
function be8() {
  return 0;
}
var et6 = class n16 extends N12 {
  constructor(t5, e4, r2) {
    super(t5.state, t5.options), this.base = t5, this.pos = e4, this.context = r2;
  }
  get node() {
    return this.context.node;
  }
  static create(t5, e4, r2) {
    return new n16(t5, e4, r2);
  }
  get textAfter() {
    return this.textAfterPos(this.pos);
  }
  get baseIndent() {
    return this.baseIndentFor(this.node);
  }
  baseIndentFor(t5) {
    let e4 = this.state.doc.lineAt(t5.from);
    for (; ; ) {
      let r2 = t5.resolve(e4.from);
      for (; r2.parent && r2.parent.from == r2.from; ) r2 = r2.parent;
      if (we8(r2, t5)) break;
      e4 = this.state.doc.lineAt(r2.from);
    }
    return this.lineIndent(e4.from);
  }
  continue() {
    return Ht5(this.context.next, this.base, this.pos);
  }
};
function we8(n22, t5) {
  for (let e4 = t5; e4; e4 = e4.parent) if (n22 == e4) return true;
  return false;
}
function ye9(n22) {
  let t5 = n22.node, e4 = t5.childAfter(t5.from), r2 = t5.lastChild;
  if (!e4) return null;
  let i9 = n22.options.simulateBreak, s99 = n22.state.doc.lineAt(e4.from), o4 = i9 == null || i9 <= s99.from ? s99.to : Math.min(s99.to, i9);
  for (let a2 = e4.to; ; ) {
    let l11 = t5.childAfter(a2);
    if (!l11 || l11 == r2) return null;
    if (!l11.type.isSkipped) {
      if (l11.from >= o4) return null;
      let f2 = /^ */.exec(s99.text.slice(e4.to - s99.from))[0].length;
      return {
        from: e4.from,
        to: e4.to + f2
      };
    }
    a2 = l11.to;
  }
}
function cn3({ closing: n22, align: t5 = true, units: e4 = 1 }) {
  return (r2) => Vt3(r2, t5, e4, n22);
}
function Vt3(n22, t5, e4, r2, i9) {
  let s99 = n22.textAfter, o4 = s99.match(/^\s*/)[0].length, a2 = r2 && s99.slice(o4, o4 + r2.length) == r2 || i9 == n22.pos + o4, l11 = t5 ? ye9(n22) : null;
  return l11 ? a2 ? n22.column(l11.from) : n22.column(l11.to) : n22.baseIndent + (a2 ? 0 : n22.unit * e4);
}
var dn3 = (n22) => n22.baseIndent;
function pn2({ except: n22, units: t5 = 1 } = {}) {
  return (e4) => {
    let r2 = n22 && n22.test(e4.textAfter);
    return e4.baseIndent + (r2 ? 0 : t5 * e4.unit);
  };
}
var ve9 = 200;
function mn2() {
  return P7.transactionFilter.of((n22) => {
    if (!n22.docChanged || !n22.isUserEvent("input.type") && !n22.isUserEvent("input.complete")) return n22;
    let t5 = n22.startState.languageDataAt("indentOnInput", n22.startState.selection.main.head);
    if (!t5.length) return n22;
    let e4 = n22.newDoc, { head: r2 } = n22.newSelection.main, i9 = e4.lineAt(r2);
    if (r2 > i9.from + ve9) return n22;
    let s99 = e4.sliceString(i9.from, r2);
    if (!t5.some((f2) => f2.test(s99))) return n22;
    let { state: o4 } = n22, a2 = -1, l11 = [];
    for (let { head: f2 } of o4.selection.ranges) {
      let h3 = o4.doc.lineAt(f2);
      if (h3.from == a2) continue;
      a2 = h3.from;
      let c4 = Wt4(o4, h3.from);
      if (c4 == null) continue;
      let w11 = /^\s*/.exec(h3.text)[0], b9 = Ut5(o4, c4);
      w11 != b9 && l11.push({
        from: h3.from,
        to: h3.from + w11.length,
        insert: b9
      });
    }
    return l11.length ? [
      n22,
      {
        changes: l11,
        sequential: true
      }
    ] : n22;
  });
}
var xe10 = k7.define();
var Te9 = new v6();
function gn3(n22) {
  let t5 = n22.firstChild, e4 = n22.lastChild;
  return t5 && t5.to < e4.from ? {
    from: t5.to,
    to: e4.type.isError ? n22.to : e4.from
  } : null;
}
function Se9(n22, t5, e4) {
  let r2 = k10(n22);
  if (r2.length < e4) return null;
  let i9 = r2.resolveStack(e4, 1), s99 = null;
  for (let o4 = i9; o4; o4 = o4.next) {
    let a2 = o4.node;
    if (a2.to <= e4 || a2.from > e4) continue;
    if (s99 && a2.from < t5) break;
    let l11 = a2.type.prop(Te9);
    if (l11 && (a2.to < r2.length - 50 || r2.length == n22.doc.length || !Pe10(a2))) {
      let f2 = l11(a2, n22);
      f2 && f2.from <= e4 && f2.from >= t5 && f2.to > e4 && (s99 = f2);
    }
  }
  return s99;
}
function Pe10(n22) {
  let t5 = n22.lastChild;
  return t5 && t5.to == n22.to && t5.type.isError;
}
function L9(n22, t5, e4) {
  for (let r2 of n22.facet(xe10)) {
    let i9 = r2(n22, t5, e4);
    if (i9) return i9;
  }
  return Se9(n22, t5, e4);
}
function $t4(n22, t5) {
  let e4 = t5.mapPos(n22.from, 1), r2 = t5.mapPos(n22.to, -1);
  return e4 >= r2 ? void 0 : {
    from: e4,
    to: r2
  };
}
var F10 = v5.define({
  map: $t4
});
var C10 = v5.define({
  map: $t4
});
function ut3(n22) {
  let t5 = [];
  for (let { head: e4 } of n22.state.selection.ranges) t5.some((r2) => r2.from <= e4 && r2.to >= e4) || t5.push(n22.lineBlockAt(e4));
  return t5;
}
var T9 = z8.define({
  create() {
    return T8.none;
  },
  update(n22, t5) {
    n22 = n22.map(t5.changes);
    for (let e4 of t5.effects) if (e4.is(F10) && !Ae8(n22, e4.value.from, e4.value.to)) {
      let { preparePlaceholder: r2 } = t5.state.facet(dt3), i9 = r2 ? T8.replace({
        widget: new nt4(r2(t5.state, e4.value))
      }) : xt5;
      n22 = n22.update({
        add: [
          i9.range(e4.value.from, e4.value.to)
        ]
      });
    } else e4.is(C10) && (n22 = n22.update({
      filter: (r2, i9) => e4.value.from != r2 || e4.value.to != i9,
      filterFrom: e4.value.from,
      filterTo: e4.value.to
    }));
    if (t5.selection) {
      let e4 = false, { head: r2 } = t5.selection.main;
      n22.between(r2, r2, (i9, s99) => {
        i9 < r2 && s99 > r2 && (e4 = true);
      }), e4 && (n22 = n22.update({
        filterFrom: r2,
        filterTo: r2,
        filter: (i9, s99) => s99 <= r2 || i9 >= r2
      }));
    }
    return n22;
  },
  provide: (n22) => k8.decorations.from(n22),
  toJSON(n22, t5) {
    let e4 = [];
    return n22.between(0, t5.doc.length, (r2, i9) => {
      e4.push(r2, i9);
    }), e4;
  },
  fromJSON(n22) {
    if (!Array.isArray(n22) || n22.length % 2) throw new RangeError("Invalid JSON for fold state");
    let t5 = [];
    for (let e4 = 0; e4 < n22.length; ) {
      let r2 = n22[e4++], i9 = n22[e4++];
      if (typeof r2 != "number" || typeof i9 != "number") throw new RangeError("Invalid JSON for fold state");
      t5.push(xt5.range(r2, i9));
    }
    return T8.set(t5, true);
  }
});
function kn3(n22) {
  return n22.field(T9, false) || T7.empty;
}
function R10(n22, t5, e4) {
  var r2;
  let i9 = null;
  return (r2 = n22.field(T9, false)) === null || r2 === void 0 || r2.between(t5, e4, (s99, o4) => {
    (!i9 || i9.from > s99) && (i9 = {
      from: s99,
      to: o4
    });
  }), i9;
}
function Ae8(n22, t5, e4) {
  let r2 = false;
  return n22.between(t5, t5, (i9, s99) => {
    i9 == t5 && s99 == e4 && (r2 = true);
  }), r2;
}
function ct5(n22, t5) {
  return n22.field(T9, false) ? t5 : t5.concat(v5.appendConfig.of(zt4()));
}
var Ce9 = (n22) => {
  for (let t5 of ut3(n22)) {
    let e4 = L9(n22.state, t5.from, t5.to);
    if (e4) return n22.dispatch({
      effects: ct5(n22.state, [
        F10.of(e4),
        $8(n22, e4)
      ])
    }), true;
  }
  return false;
};
var Ie9 = (n22) => {
  if (!n22.state.field(T9, false)) return false;
  let t5 = [];
  for (let e4 of ut3(n22)) {
    let r2 = R10(n22.state, e4.from, e4.to);
    r2 && t5.push(C10.of(r2), $8(n22, r2, false));
  }
  return t5.length && n22.dispatch({
    effects: t5
  }), t5.length > 0;
};
function $8(n22, t5, e4 = true) {
  let r2 = n22.state.doc.lineAt(t5.from).number, i9 = n22.state.doc.lineAt(t5.to).number;
  return k8.announce.of(`${n22.state.phrase(e4 ? "Folded lines" : "Unfolded lines")} ${r2} ${n22.state.phrase("to")} ${i9}.`);
}
var De9 = (n22) => {
  let { state: t5 } = n22, e4 = [];
  for (let r2 = 0; r2 < t5.doc.length; ) {
    let i9 = n22.lineBlockAt(r2), s99 = L9(t5, i9.from, i9.to);
    s99 && e4.push(F10.of(s99)), r2 = (s99 ? n22.lineBlockAt(s99.to) : i9).to + 1;
  }
  return e4.length && n22.dispatch({
    effects: ct5(n22.state, e4)
  }), !!e4.length;
};
var Oe8 = (n22) => {
  let t5 = n22.state.field(T9, false);
  if (!t5 || !t5.size) return false;
  let e4 = [];
  return t5.between(0, n22.state.doc.length, (r2, i9) => {
    e4.push(C10.of({
      from: r2,
      to: i9
    }));
  }), n22.dispatch({
    effects: e4
  }), true;
};
function Me8(n22, t5) {
  for (let e4 = t5; ; ) {
    let r2 = L9(n22.state, e4.from, e4.to);
    if (r2 && r2.to > t5.from) return r2;
    if (!e4.from) return null;
    e4 = n22.lineBlockAt(e4.from - 1);
  }
}
var bn3 = (n22) => {
  let t5 = [];
  for (let e4 of ut3(n22)) {
    let r2 = R10(n22.state, e4.from, e4.to);
    if (r2) t5.push(C10.of(r2), $8(n22, r2, false));
    else {
      let i9 = Me8(n22, e4);
      i9 && t5.push(F10.of(i9), $8(n22, i9));
    }
  }
  return t5.length > 0 && n22.dispatch({
    effects: ct5(n22.state, t5)
  }), !!t5.length;
};
var wn3 = [
  {
    key: "Ctrl-Shift-[",
    mac: "Cmd-Alt-[",
    run: Ce9
  },
  {
    key: "Ctrl-Shift-]",
    mac: "Cmd-Alt-]",
    run: Ie9
  },
  {
    key: "Ctrl-Alt-[",
    run: De9
  },
  {
    key: "Ctrl-Alt-]",
    run: Oe8
  }
];
var Be8 = {
  placeholderDOM: null,
  preparePlaceholder: null,
  placeholderText: "\u2026"
};
var dt3 = k7.define({
  combine(n22) {
    return rt4(n22, Be8);
  }
});
function zt4(n22) {
  let t5 = [
    T9,
    Le9
  ];
  return n22 && t5.push(dt3.of(n22)), t5;
}
function qt4(n22, t5) {
  let { state: e4 } = n22, r2 = e4.facet(dt3), i9 = (o4) => {
    let a2 = n22.lineBlockAt(n22.posAtDOM(o4.target)), l11 = R10(n22.state, a2.from, a2.to);
    l11 && n22.dispatch({
      effects: C10.of(l11)
    }), o4.preventDefault();
  };
  if (r2.placeholderDOM) return r2.placeholderDOM(n22, i9, t5);
  let s99 = document.createElement("span");
  return s99.textContent = r2.placeholderText, s99.setAttribute("aria-label", e4.phrase("folded code")), s99.title = e4.phrase("unfold"), s99.className = "cm-foldPlaceholder", s99.onclick = i9, s99;
}
var xt5 = T8.replace({
  widget: new class extends et4 {
    toDOM(n22) {
      return qt4(n22, null);
    }
  }()
});
var nt4 = class extends et4 {
  constructor(t5) {
    super(), this.value = t5;
  }
  eq(t5) {
    return this.value == t5.value;
  }
  toDOM(t5) {
    return qt4(t5, this.value);
  }
};
var Ne7 = {
  openText: "\u2304",
  closedText: "\u203A",
  markerDOM: null,
  domEventHandlers: {},
  foldingChanged: () => false
};
var O8 = class extends Q9 {
  constructor(t5, e4) {
    super(), this.config = t5, this.open = e4;
  }
  eq(t5) {
    return this.config == t5.config && this.open == t5.open;
  }
  toDOM(t5) {
    if (this.config.markerDOM) return this.config.markerDOM(this.open);
    let e4 = document.createElement("span");
    return e4.textContent = this.open ? this.config.openText : this.config.closedText, e4.title = t5.state.phrase(this.open ? "Fold line" : "Unfold line"), e4;
  }
};
function yn3(n22 = {}) {
  let t5 = Object.assign(Object.assign({}, Ne7), n22), e4 = new O8(t5, true), r2 = new O8(t5, false), i9 = N10.fromClass(class {
    constructor(o4) {
      this.from = o4.viewport.from, this.markers = this.buildMarkers(o4);
    }
    update(o4) {
      (o4.docChanged || o4.viewportChanged || o4.startState.facet(x9) != o4.state.facet(x9) || o4.startState.field(T9, false) != o4.state.field(T9, false) || k10(o4.startState) != k10(o4.state) || t5.foldingChanged(o4)) && (this.markers = this.buildMarkers(o4.view));
    }
    buildMarkers(o4) {
      let a2 = new re7();
      for (let l11 of o4.viewportLineBlocks) {
        let f2 = R10(o4.state, l11.from, l11.to) ? r2 : L9(o4.state, l11.from, l11.to) ? e4 : null;
        f2 && a2.add(l11.from, l11.from, f2);
      }
      return a2.finish();
    }
  }), { domEventHandlers: s99 } = t5;
  return [
    i9,
    Fl({
      class: "cm-foldGutter",
      markers(o4) {
        var a2;
        return ((a2 = o4.plugin(i9)) === null || a2 === void 0 ? void 0 : a2.markers) || T7.empty;
      },
      initialSpacer() {
        return new O8(t5, false);
      },
      domEventHandlers: Object.assign(Object.assign({}, s99), {
        click: (o4, a2, l11) => {
          if (s99.click && s99.click(o4, a2, l11)) return true;
          let f2 = R10(o4.state, a2.from, a2.to);
          if (f2) return o4.dispatch({
            effects: C10.of(f2)
          }), true;
          let h3 = L9(o4.state, a2.from, a2.to);
          return h3 ? (o4.dispatch({
            effects: F10.of(h3)
          }), true) : false;
        }
      })
    }),
    zt4()
  ];
}
var Le9 = k8.baseTheme({
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
var z11 = class n17 {
  constructor(t5, e4) {
    this.specs = t5;
    let r2;
    function i9(a2) {
      let l11 = T2.newName();
      return (r2 || (r2 = /* @__PURE__ */ Object.create(null)))["." + l11] = a2, l11;
    }
    let s99 = typeof e4.all == "string" ? e4.all : e4.all ? i9(e4.all) : void 0, o4 = e4.scope;
    this.scope = o4 instanceof d3 ? (a2) => a2.prop(S8) == o4.data : o4 ? (a2) => a2 == o4 : void 0, this.style = U10(t5.map((a2) => ({
      tag: a2.tag,
      class: a2.class || i9(Object.assign({}, a2, {
        tag: null
      }))
    })), {
      all: s99
    }).style, this.module = r2 ? new T2(r2) : null, this.themeType = e4.themeType;
  }
  static define(t5, e4) {
    return new n17(t5, e4 || {});
  }
};
var rt6 = k7.define();
var Gt4 = k7.define({
  combine(n22) {
    return n22.length ? [
      n22[0]
    ] : null;
  }
});
function j10(n22) {
  let t5 = n22.facet(rt6);
  return t5.length ? t5 : n22.facet(Gt4);
}
function vn3(n22, t5) {
  let e4 = [
    Re8
  ], r2;
  return n22 instanceof z11 && (n22.module && e4.push(k8.styleModule.of(n22.module)), r2 = n22.themeType), t5?.fallback ? e4.push(Gt4.of(n22)) : r2 ? e4.push(rt6.computeN([
    k8.darkTheme
  ], (i9) => i9.facet(k8.darkTheme) == (r2 == "dark") ? [
    n22
  ] : [])) : e4.push(rt6.of(n22)), e4;
}
function xn3(n22, t5, e4) {
  let r2 = j10(n22), i9 = null;
  if (r2) {
    for (let s99 of r2) if (!s99.scope || e4 && s99.scope(e4)) {
      let o4 = s99.style(t5);
      o4 && (i9 = i9 ? i9 + " " + o4 : o4);
    }
  }
  return i9;
}
var it7 = class {
  constructor(t5) {
    this.markCache = /* @__PURE__ */ Object.create(null), this.tree = k10(t5.state), this.decorations = this.buildDeco(t5, j10(t5.state)), this.decoratedTo = t5.viewport.to;
  }
  update(t5) {
    let e4 = k10(t5.state), r2 = j10(t5.state), i9 = r2 != j10(t5.startState), { viewport: s99 } = t5.view, o4 = t5.changes.mapPos(this.decoratedTo, 1);
    e4.length < s99.to && !i9 && e4.type == this.tree.type && o4 >= s99.to ? (this.decorations = this.decorations.map(t5.changes), this.decoratedTo = o4) : (e4 != this.tree || t5.viewportChanged || i9) && (this.tree = e4, this.decorations = this.buildDeco(t5.view, r2), this.decoratedTo = s99.to);
  }
  buildDeco(t5, e4) {
    if (!e4 || !this.tree.length) return T8.none;
    let r2 = new re7();
    for (let { from: i9, to: s99 } of t5.visibleRanges) X10(this.tree, e4, (o4, a2, l11) => {
      r2.add(o4, a2, this.markCache[l11] || (this.markCache[l11] = T8.mark({
        class: l11
      })));
    }, i9, s99);
    return r2.finish();
  }
};
var Re8 = st4.high(N10.fromClass(it7, {
  decorations: (n22) => n22.decorations
}));
var Tn4 = z11.define([
  {
    tag: l10.meta,
    color: "#404740"
  },
  {
    tag: l10.link,
    textDecoration: "underline"
  },
  {
    tag: l10.heading,
    textDecoration: "underline",
    fontWeight: "bold"
  },
  {
    tag: l10.emphasis,
    fontStyle: "italic"
  },
  {
    tag: l10.strong,
    fontWeight: "bold"
  },
  {
    tag: l10.strikethrough,
    textDecoration: "line-through"
  },
  {
    tag: l10.keyword,
    color: "#708"
  },
  {
    tag: [
      l10.atom,
      l10.bool,
      l10.url,
      l10.contentSeparator,
      l10.labelName
    ],
    color: "#219"
  },
  {
    tag: [
      l10.literal,
      l10.inserted
    ],
    color: "#164"
  },
  {
    tag: [
      l10.string,
      l10.deleted
    ],
    color: "#a11"
  },
  {
    tag: [
      l10.regexp,
      l10.escape,
      l10.special(l10.string)
    ],
    color: "#e40"
  },
  {
    tag: l10.definition(l10.variableName),
    color: "#00f"
  },
  {
    tag: l10.local(l10.variableName),
    color: "#30a"
  },
  {
    tag: [
      l10.typeName,
      l10.namespace
    ],
    color: "#085"
  },
  {
    tag: l10.className,
    color: "#167"
  },
  {
    tag: [
      l10.special(l10.variableName),
      l10.macroName
    ],
    color: "#256"
  },
  {
    tag: l10.definition(l10.propertyName),
    color: "#00c"
  },
  {
    tag: l10.comment,
    color: "#940"
  },
  {
    tag: l10.invalid,
    color: "#f00"
  }
]);
var Ee8 = k8.baseTheme({
  "&.cm-focused .cm-matchingBracket": {
    backgroundColor: "#328c8252"
  },
  "&.cm-focused .cm-nonmatchingBracket": {
    backgroundColor: "#bb555544"
  }
});
var Jt4 = 1e4;
var _t4 = "()[]{}";
var Kt4 = k7.define({
  combine(n22) {
    return rt4(n22, {
      afterCursor: true,
      brackets: _t4,
      maxScanDistance: Jt4,
      renderMatch: We7
    });
  }
});
var Fe8 = T8.mark({
  class: "cm-matchingBracket"
});
var Ue7 = T8.mark({
  class: "cm-nonmatchingBracket"
});
function We7(n22) {
  let t5 = [], e4 = n22.matched ? Fe8 : Ue7;
  return t5.push(e4.range(n22.start.from, n22.start.to)), n22.end && t5.push(e4.range(n22.end.from, n22.end.to)), t5;
}
var je6 = z8.define({
  create() {
    return T8.none;
  },
  update(n22, t5) {
    if (!t5.docChanged && !t5.selection) return n22;
    let e4 = [], r2 = t5.state.facet(Kt4);
    for (let i9 of t5.state.selection.ranges) {
      if (!i9.empty) continue;
      let s99 = U11(t5.state, i9.head, -1, r2) || i9.head > 0 && U11(t5.state, i9.head - 1, 1, r2) || r2.afterCursor && (U11(t5.state, i9.head, 1, r2) || i9.head < t5.state.doc.length && U11(t5.state, i9.head + 1, -1, r2));
      s99 && (e4 = e4.concat(r2.renderMatch(s99, t5.state)));
    }
    return T8.set(e4, true);
  },
  provide: (n22) => k8.decorations.from(n22)
});
var He6 = [
  je6,
  Ee8
];
function Sn3(n22 = {}) {
  return [
    Kt4.of(n22),
    He6
  ];
}
var Ve6 = new v6();
function st5(n22, t5, e4) {
  let r2 = n22.prop(t5 < 0 ? v6.openedBy : v6.closedBy);
  if (r2) return r2;
  if (n22.name.length == 1) {
    let i9 = e4.indexOf(n22.name);
    if (i9 > -1 && i9 % 2 == (t5 < 0 ? 1 : 0)) return [
      e4[i9 + t5]
    ];
  }
  return null;
}
function ot6(n22) {
  let t5 = n22.type.prop(Ve6);
  return t5 ? t5(n22.node) : n22;
}
function U11(n22, t5, e4, r2 = {}) {
  let i9 = r2.maxScanDistance || Jt4, s99 = r2.brackets || _t4, o4 = k10(n22), a2 = o4.resolveInner(t5, e4);
  for (let l11 = a2; l11; l11 = l11.parent) {
    let f2 = st5(l11.type, e4, s99);
    if (f2 && l11.from < l11.to) {
      let h3 = ot6(l11);
      if (h3 && (e4 > 0 ? t5 >= h3.from && t5 < h3.to : t5 > h3.from && t5 <= h3.to)) return $e5(n22, t5, e4, l11, h3, f2, s99);
    }
  }
  return ze8(n22, t5, e4, o4, a2.type, i9, s99);
}
function $e5(n22, t5, e4, r2, i9, s99, o4) {
  let a2 = r2.parent, l11 = {
    from: i9.from,
    to: i9.to
  }, f2 = 0, h3 = a2?.cursor();
  if (h3 && (e4 < 0 ? h3.childBefore(r2.from) : h3.childAfter(r2.to))) do
    if (e4 < 0 ? h3.to <= r2.from : h3.from >= r2.to) {
      if (f2 == 0 && s99.indexOf(h3.type.name) > -1 && h3.from < h3.to) {
        let c4 = ot6(h3);
        return {
          start: l11,
          end: c4 ? {
            from: c4.from,
            to: c4.to
          } : void 0,
          matched: true
        };
      } else if (st5(h3.type, e4, o4)) f2++;
      else if (st5(h3.type, -e4, o4)) {
        if (f2 == 0) {
          let c4 = ot6(h3);
          return {
            start: l11,
            end: c4 && c4.from < c4.to ? {
              from: c4.from,
              to: c4.to
            } : void 0,
            matched: false
          };
        }
        f2--;
      }
    }
  while (e4 < 0 ? h3.prevSibling() : h3.nextSibling());
  return {
    start: l11,
    matched: false
  };
}
function ze8(n22, t5, e4, r2, i9, s99, o4) {
  let a2 = e4 < 0 ? n22.sliceDoc(t5 - 1, t5) : n22.sliceDoc(t5, t5 + 1), l11 = o4.indexOf(a2);
  if (l11 < 0 || l11 % 2 == 0 != e4 > 0) return null;
  let f2 = {
    from: e4 < 0 ? t5 - 1 : t5,
    to: e4 > 0 ? t5 + 1 : t5
  }, h3 = n22.doc.iterRange(t5, e4 > 0 ? n22.doc.length : 0), c4 = 0;
  for (let w11 = 0; !h3.next().done && w11 <= s99; ) {
    let b9 = h3.value;
    e4 < 0 && (w11 += b9.length);
    let P12 = t5 + w11 * e4;
    for (let A11 = e4 > 0 ? 0 : b9.length - 1, ne11 = e4 > 0 ? b9.length : -1; A11 != ne11; A11 += e4) {
      let Q13 = o4.indexOf(b9[A11]);
      if (!(Q13 < 0 || r2.resolveInner(P12 + A11, 1).type != i9)) if (Q13 % 2 == 0 == e4 > 0) c4++;
      else {
        if (c4 == 1) return {
          start: f2,
          end: {
            from: P12 + A11,
            to: P12 + A11 + 1
          },
          matched: Q13 >> 1 == l11 >> 1
        };
        c4--;
      }
    }
    e4 > 0 && (w11 += b9.length);
  }
  return h3.done ? {
    start: f2,
    matched: false
  } : null;
}
function Tt6(n22, t5, e4, r2 = 0, i9 = 0) {
  t5 == null && (t5 = n22.search(/[^\s\u00a0]/), t5 == -1 && (t5 = n22.length));
  let s99 = i9;
  for (let o4 = r2; o4 < t5; o4++) n22.charCodeAt(o4) == 9 ? s99 += e4 - s99 % e4 : s99++;
  return s99;
}
var q11 = class {
  constructor(t5, e4, r2, i9) {
    this.string = t5, this.tabSize = e4, this.indentUnit = r2, this.overrideIndent = i9, this.pos = 0, this.start = 0, this.lastColumnPos = 0, this.lastColumnValue = 0;
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
  eat(t5) {
    let e4 = this.string.charAt(this.pos), r2;
    if (typeof t5 == "string" ? r2 = e4 == t5 : r2 = e4 && (t5 instanceof RegExp ? t5.test(e4) : t5(e4)), r2) return ++this.pos, e4;
  }
  eatWhile(t5) {
    let e4 = this.pos;
    for (; this.eat(t5); ) ;
    return this.pos > e4;
  }
  eatSpace() {
    let t5 = this.pos;
    for (; /[\s\u00a0]/.test(this.string.charAt(this.pos)); ) ++this.pos;
    return this.pos > t5;
  }
  skipToEnd() {
    this.pos = this.string.length;
  }
  skipTo(t5) {
    let e4 = this.string.indexOf(t5, this.pos);
    if (e4 > -1) return this.pos = e4, true;
  }
  backUp(t5) {
    this.pos -= t5;
  }
  column() {
    return this.lastColumnPos < this.start && (this.lastColumnValue = Tt6(this.string, this.start, this.tabSize, this.lastColumnPos, this.lastColumnValue), this.lastColumnPos = this.start), this.lastColumnValue;
  }
  indentation() {
    var t5;
    return (t5 = this.overrideIndent) !== null && t5 !== void 0 ? t5 : Tt6(this.string, null, this.tabSize);
  }
  match(t5, e4, r2) {
    if (typeof t5 == "string") {
      let i9 = (o4) => r2 ? o4.toLowerCase() : o4, s99 = this.string.substr(this.pos, t5.length);
      return i9(s99) == i9(t5) ? (e4 !== false && (this.pos += t5.length), true) : null;
    } else {
      let i9 = this.string.slice(this.pos).match(t5);
      return i9 && i9.index > 0 ? null : (i9 && e4 !== false && (this.pos += i9[0].length), i9);
    }
  }
  current() {
    return this.string.slice(this.start, this.pos);
  }
};
function qe7(n22) {
  return {
    name: n22.name || "",
    token: n22.token,
    blankLine: n22.blankLine || (() => {
    }),
    startState: n22.startState || (() => true),
    copyState: n22.copyState || Ge6,
    indent: n22.indent || (() => null),
    languageData: n22.languageData || {},
    tokenTable: n22.tokenTable || mt5,
    mergeTokens: n22.mergeTokens !== false
  };
}
function Ge6(n22) {
  if (typeof n22 != "object") return n22;
  let t5 = {};
  for (let e4 in n22) {
    let r2 = n22[e4];
    t5[e4] = r2 instanceof Array ? r2.slice() : r2;
  }
  return t5;
}
var St5 = /* @__PURE__ */ new WeakMap();
var Pt5 = class n18 extends d3 {
  constructor(t5) {
    let e4 = Lt6(t5.languageData), r2 = qe7(t5), i9, s99 = new class extends Ae7 {
      createParse(o4, a2, l11) {
        return new lt5(i9, o4, a2, l11);
      }
    }();
    super(e4, s99, [], t5.name), this.topNode = Qe6(e4, this), i9 = this, this.streamParser = r2, this.stateAfter = new v6({
      perNode: true
    }), this.tokenTable = t5.tokenTable ? new G10(r2.tokenTable) : Ke6;
  }
  static define(t5) {
    return new n18(t5);
  }
  getIndent(t5) {
    let e4, { overrideIndentation: r2 } = t5.options;
    r2 && (e4 = St5.get(t5.state), e4 != null && e4 < t5.pos - 1e4 && (e4 = void 0));
    let i9 = pt5(this, t5.node.tree, t5.node.from, t5.node.from, e4 ?? t5.pos), s99, o4;
    if (i9 ? (o4 = i9.state, s99 = i9.pos + 1) : (o4 = this.streamParser.startState(t5.unit), s99 = t5.node.from), t5.pos - s99 > 1e4) return null;
    for (; s99 < t5.pos; ) {
      let l11 = t5.state.doc.lineAt(s99), f2 = Math.min(t5.pos, l11.to);
      if (l11.length) {
        let h3 = r2 ? r2(l11.from) : -1, c4 = new q11(l11.text, t5.state.tabSize, t5.unit, h3 < 0 ? void 0 : h3);
        for (; c4.pos < f2 - l11.from; ) Xt5(this.streamParser.token, c4, o4);
      } else this.streamParser.blankLine(o4, t5.unit);
      if (f2 == t5.pos) break;
      s99 = l11.to + 1;
    }
    let a2 = t5.lineAt(t5.pos);
    return r2 && e4 == null && St5.set(t5.state, a2.from), this.streamParser.indent(o4, /^\s*(.*)/.exec(a2.text)[1], t5);
  }
  get allowsNesting() {
    return false;
  }
};
function pt5(n22, t5, e4, r2, i9) {
  let s99 = e4 >= r2 && e4 + t5.length <= i9 && t5.prop(n22.stateAfter);
  if (s99) return {
    state: n22.streamParser.copyState(s99),
    pos: e4 + t5.length
  };
  for (let o4 = t5.children.length - 1; o4 >= 0; o4--) {
    let a2 = t5.children[o4], l11 = e4 + t5.positions[o4], f2 = a2 instanceof E7 && l11 < i9 && pt5(n22, a2, l11, r2, i9);
    if (f2) return f2;
  }
  return null;
}
function Qt5(n22, t5, e4, r2, i9) {
  if (i9 && e4 <= 0 && r2 >= t5.length) return t5;
  !i9 && e4 == 0 && t5.type == n22.topNode && (i9 = true);
  for (let s99 = t5.children.length - 1; s99 >= 0; s99--) {
    let o4 = t5.positions[s99], a2 = t5.children[s99], l11;
    if (o4 < r2 && a2 instanceof E7) {
      if (!(l11 = Qt5(n22, a2, e4 - o4, r2 - o4, i9))) break;
      return i9 ? new E7(t5.type, t5.children.slice(0, s99).concat(l11), t5.positions.slice(0, s99 + 1), o4 + l11.length) : l11;
    }
  }
  return null;
}
function Je7(n22, t5, e4, r2, i9) {
  for (let s99 of t5) {
    let o4 = s99.from + (s99.openStart ? 25 : 0), a2 = s99.to - (s99.openEnd ? 25 : 0), l11 = o4 <= e4 && a2 > e4 && pt5(n22, s99.tree, 0 - s99.offset, e4, a2), f2;
    if (l11 && l11.pos <= r2 && (f2 = Qt5(n22, s99.tree, e4 + s99.offset, l11.pos + s99.offset, false))) return {
      state: l11.state,
      tree: f2
    };
  }
  return {
    state: n22.streamParser.startState(i9 ? V11(i9) : 4),
    tree: E7.empty
  };
}
var lt5 = class {
  constructor(t5, e4, r2, i9) {
    this.lang = t5, this.input = e4, this.fragments = r2, this.ranges = i9, this.stoppedAt = null, this.chunks = [], this.chunkPos = [], this.chunk = [], this.chunkReused = void 0, this.rangeIndex = 0, this.to = i9[i9.length - 1].to;
    let s99 = M11.get(), o4 = i9[0].from, { state: a2, tree: l11 } = Je7(t5, r2, o4, this.to, s99?.state);
    this.state = a2, this.parsedPos = this.chunkStart = o4 + l11.length;
    for (let f2 = 0; f2 < l11.children.length; f2++) this.chunks.push(l11.children[f2]), this.chunkPos.push(l11.positions[f2]);
    s99 && this.parsedPos < s99.viewport.from - 1e5 && i9.some((f2) => f2.from <= s99.viewport.from && f2.to >= s99.viewport.from) && (this.state = this.lang.streamParser.startState(V11(s99.state)), s99.skipUntilInView(this.parsedPos, s99.viewport.from), this.parsedPos = s99.viewport.from), this.moveRangeIndex();
  }
  advance() {
    let t5 = M11.get(), e4 = this.stoppedAt == null ? this.to : Math.min(this.to, this.stoppedAt), r2 = Math.min(e4, this.chunkStart + 2048);
    for (t5 && (r2 = Math.min(r2, t5.viewport.to)); this.parsedPos < r2; ) this.parseLine(t5);
    return this.chunkStart < this.parsedPos && this.finishChunk(), this.parsedPos >= e4 ? this.finish() : t5 && this.parsedPos >= t5.viewport.to ? (t5.skipUntilInView(this.parsedPos, e4), this.finish()) : null;
  }
  stopAt(t5) {
    this.stoppedAt = t5;
  }
  lineAfter(t5) {
    let e4 = this.input.chunk(t5);
    if (this.input.lineChunks) e4 == `
` && (e4 = "");
    else {
      let r2 = e4.indexOf(`
`);
      r2 > -1 && (e4 = e4.slice(0, r2));
    }
    return t5 + e4.length <= this.to ? e4 : e4.slice(0, this.to - t5);
  }
  nextLine() {
    let t5 = this.parsedPos, e4 = this.lineAfter(t5), r2 = t5 + e4.length;
    for (let i9 = this.rangeIndex; ; ) {
      let s99 = this.ranges[i9].to;
      if (s99 >= r2 || (e4 = e4.slice(0, s99 - (r2 - e4.length)), i9++, i9 == this.ranges.length)) break;
      let o4 = this.ranges[i9].from, a2 = this.lineAfter(o4);
      e4 += a2, r2 = o4 + a2.length;
    }
    return {
      line: e4,
      end: r2
    };
  }
  skipGapsTo(t5, e4, r2) {
    for (; ; ) {
      let i9 = this.ranges[this.rangeIndex].to, s99 = t5 + e4;
      if (r2 > 0 ? i9 > s99 : i9 >= s99) break;
      let o4 = this.ranges[++this.rangeIndex].from;
      e4 += o4 - i9;
    }
    return e4;
  }
  moveRangeIndex() {
    for (; this.ranges[this.rangeIndex].to < this.parsedPos; ) this.rangeIndex++;
  }
  emitToken(t5, e4, r2, i9) {
    let s99 = 4;
    if (this.ranges.length > 1) {
      i9 = this.skipGapsTo(e4, i9, 1), e4 += i9;
      let a2 = this.chunk.length;
      i9 = this.skipGapsTo(r2, i9, -1), r2 += i9, s99 += this.chunk.length - a2;
    }
    let o4 = this.chunk.length - 4;
    return this.lang.streamParser.mergeTokens && s99 == 4 && o4 >= 0 && this.chunk[o4] == t5 && this.chunk[o4 + 2] == e4 ? this.chunk[o4 + 2] = r2 : this.chunk.push(t5, e4, r2, s99), i9;
  }
  parseLine(t5) {
    let { line: e4, end: r2 } = this.nextLine(), i9 = 0, { streamParser: s99 } = this.lang, o4 = new q11(e4, t5 ? t5.state.tabSize : 4, t5 ? V11(t5.state) : 2);
    if (o4.eol()) s99.blankLine(this.state, o4.indentUnit);
    else for (; !o4.eol(); ) {
      let a2 = Xt5(s99.token, o4, this.state);
      if (a2 && (i9 = this.emitToken(this.lang.tokenTable.resolve(a2), this.parsedPos + o4.start, this.parsedPos + o4.pos, i9)), o4.start > 1e4) break;
    }
    this.parsedPos = r2, this.moveRangeIndex(), this.parsedPos < this.to && this.parsedPos++;
  }
  finishChunk() {
    let t5 = E7.build({
      buffer: this.chunk,
      start: this.chunkStart,
      length: this.parsedPos - this.chunkStart,
      nodeSet: _e8,
      topID: 0,
      maxBufferLength: 2048,
      reused: this.chunkReused
    });
    t5 = new E7(t5.type, t5.children, t5.positions, t5.length, [
      [
        this.lang.stateAfter,
        this.lang.streamParser.copyState(this.state)
      ]
    ]), this.chunks.push(t5), this.chunkPos.push(this.chunkStart - this.ranges[0].from), this.chunk = [], this.chunkReused = void 0, this.chunkStart = this.parsedPos;
  }
  finish() {
    return new E7(this.lang.topNode, this.chunks, this.chunkPos, this.parsedPos - this.ranges[0].from).balance();
  }
};
function Xt5(n22, t5, e4) {
  t5.start = t5.pos;
  for (let r2 = 0; r2 < 10; r2++) {
    let i9 = n22(t5, e4);
    if (t5.pos > t5.start) return i9;
  }
  throw new Error("Stream parser failed to advance stream.");
}
var mt5 = /* @__PURE__ */ Object.create(null);
var E9 = [
  M10.none
];
var _e8 = new ye8(E9);
var At4 = [];
var Ct6 = /* @__PURE__ */ Object.create(null);
var Yt4 = /* @__PURE__ */ Object.create(null);
for (let [n22, t5] of [
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
    "tagName"
  ],
  [
    "attribute",
    "attributeName"
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
]) Yt4[n22] = Zt4(mt5, t5);
var G10 = class {
  constructor(t5) {
    this.extra = t5, this.table = Object.assign(/* @__PURE__ */ Object.create(null), Yt4);
  }
  resolve(t5) {
    return t5 ? this.table[t5] || (this.table[t5] = Zt4(this.extra, t5)) : 0;
  }
};
var Ke6 = new G10(mt5);
function Z11(n22, t5) {
  At4.indexOf(n22) > -1 || (At4.push(n22), console.warn(t5));
}
function Zt4(n22, t5) {
  let e4 = [];
  for (let a2 of t5.split(" ")) {
    let l11 = [];
    for (let f2 of a2.split(".")) {
      let h3 = n22[f2] || l10[f2];
      h3 ? typeof h3 == "function" ? l11.length ? l11 = l11.map(h3) : Z11(f2, `Modifier ${f2} used at start of tag`) : l11.length ? Z11(f2, `Tag ${f2} used as modifier`) : l11 = Array.isArray(h3) ? h3 : [
        h3
      ] : Z11(f2, `Unknown highlighting tag ${f2}`);
    }
    for (let f2 of l11) e4.push(f2);
  }
  if (!e4.length) return 0;
  let r2 = t5.replace(/ /g, "_"), i9 = r2 + " " + e4.map((a2) => a2.id), s99 = Ct6[i9];
  if (s99) return s99.id;
  let o4 = Ct6[i9] = M10.define({
    id: E9.length,
    name: r2,
    props: [
      _9({
        [r2]: e4
      })
    ]
  });
  return E9.push(o4), o4.id;
}
function Qe6(n22, t5) {
  let e4 = M10.define({
    id: E9.length,
    name: "Document",
    props: [
      S8.add(() => n22),
      jt6.add(() => (r2) => t5.getIndent(r2))
    ],
    top: true
  });
  return E9.push(e4), e4;
}
function te10(n22) {
  return n22.length <= 4096 && /[\u0590-\u05f4\u0600-\u06ff\u0700-\u08ac\ufb50-\ufdff]/.test(n22);
}
function ee9(n22) {
  for (let t5 = n22.iter(); !t5.next().done; ) if (te10(t5.value)) return true;
  return false;
}
function Xe7(n22) {
  let t5 = false;
  return n22.iterChanges((e4, r2, i9, s99, o4) => {
    !t5 && ee9(o4) && (t5 = true);
  }), t5;
}
var at7 = k7.define({
  combine: (n22) => n22.some((t5) => t5)
});
function Pn3(n22 = {}) {
  let t5 = [
    Ye7
  ];
  return n22.alwaysIsolate && t5.push(at7.of(true)), t5;
}
var Ye7 = N10.fromClass(class {
  constructor(n22) {
    this.always = n22.state.facet(at7) || n22.textDirection != R9.LTR || n22.state.facet(k8.perLineTextDirection), this.hasRTL = !this.always && ee9(n22.state.doc), this.tree = k10(n22.state), this.decorations = this.always || this.hasRTL ? It5(n22, this.tree, this.always) : T8.none;
  }
  update(n22) {
    let t5 = n22.state.facet(at7) || n22.view.textDirection != R9.LTR || n22.state.facet(k8.perLineTextDirection);
    if (!t5 && !this.hasRTL && Xe7(n22.changes) && (this.hasRTL = true), !t5 && !this.hasRTL) return;
    let e4 = k10(n22.state);
    (t5 != this.always || e4 != this.tree || n22.docChanged || n22.viewportChanged) && (this.tree = e4, this.always = t5, this.decorations = It5(n22.view, e4, t5));
  }
}, {
  provide: (n22) => {
    function t5(e4) {
      var r2, i9;
      return (i9 = (r2 = e4.plugin(n22)) === null || r2 === void 0 ? void 0 : r2.decorations) !== null && i9 !== void 0 ? i9 : T8.none;
    }
    return [
      k8.outerDecorations.of(t5),
      st4.lowest(k8.bidiIsolatedRanges.of(t5))
    ];
  }
});
function It5(n22, t5, e4) {
  let r2 = new re7(), i9 = n22.visibleRanges;
  e4 || (i9 = Ze5(i9, n22.state.doc));
  for (let { from: s99, to: o4 } of i9) t5.iterate({
    enter: (a2) => {
      let l11 = a2.type.prop(v6.isolate);
      l11 && r2.add(a2.from, a2.to, tn4[l11]);
    },
    from: s99,
    to: o4
  });
  return r2.finish();
}
function Ze5(n22, t5) {
  let e4 = t5.iter(), r2 = 0, i9 = [], s99 = null;
  for (let { from: o4, to: a2 } of n22) if (!(s99 && s99.to > o4 && (o4 = s99.to, o4 >= a2))) for (r2 + e4.value.length < o4 && (e4.next(o4 - (r2 + e4.value.length)), r2 = o4); ; ) {
    let l11 = r2, f2 = r2 + e4.value.length;
    if (!e4.lineBreak && te10(e4.value) && (s99 && s99.to > l11 - 10 ? s99.to = Math.min(a2, f2) : i9.push(s99 = {
      from: l11,
      to: Math.min(a2, f2)
    })), f2 >= a2) break;
    r2 = f2, e4.next();
  }
  return i9;
}
var tn4 = {
  rtl: T8.mark({
    class: "cm-iso",
    inclusive: true,
    attributes: {
      dir: "rtl"
    },
    bidiIsolate: R9.RTL
  }),
  ltr: T8.mark({
    class: "cm-iso",
    inclusive: true,
    attributes: {
      dir: "ltr"
    },
    bidiIsolate: R9.LTR
  }),
  auto: T8.mark({
    class: "cm-iso",
    inclusive: true,
    attributes: {
      dir: "auto"
    },
    bidiIsolate: null
  })
};

// deno:https://esm.sh/@codemirror/language@6.12.1/denonext/language.mjs
var X12;
var S9 = new v6();
var de11 = new v6();
var d4 = class {
  constructor(t5, e4, r2 = [], i9 = "") {
    this.data = t5, this.name = i9, P7.prototype.hasOwnProperty("tree") || Object.defineProperty(P7.prototype, "tree", {
      get() {
        return k11(this);
      }
    }), this.parser = e4, this.extension = [
      x10.of(this),
      P7.languageData.of((s99, o4, a2) => {
        let l11 = bt6(s99, o4, a2), h3 = l11.type.prop(S9);
        if (!h3) return [];
        let f2 = s99.facet(h3), c4 = l11.type.prop(de11);
        if (c4) {
          let w11 = l11.resolve(o4 - l11.from, a2);
          for (let b9 of c4) if (b9.test(w11, s99)) {
            let P12 = s99.facet(b9.facet);
            return b9.type == "replace" ? P12 : P12.concat(f2);
          }
        }
        return f2;
      })
    ].concat(r2);
  }
  isActiveAt(t5, e4, r2 = -1) {
    return bt6(t5, e4, r2).type.prop(S9) == this.data;
  }
  findRegions(t5) {
    let e4 = t5.facet(x10);
    if (e4?.data == this.data) return [
      {
        from: 0,
        to: t5.doc.length
      }
    ];
    if (!e4 || !e4.allowsNesting) return [];
    let r2 = [], i9 = (s99, o4) => {
      if (s99.prop(S9) == this.data) {
        r2.push({
          from: o4,
          to: o4 + s99.length
        });
        return;
      }
      let a2 = s99.prop(v6.mounted);
      if (a2) {
        if (a2.tree.prop(S9) == this.data) {
          if (a2.overlay) for (let l11 of a2.overlay) r2.push({
            from: l11.from + o4,
            to: l11.to + o4
          });
          else r2.push({
            from: o4,
            to: o4 + s99.length
          });
          return;
        } else if (a2.overlay) {
          let l11 = r2.length;
          if (i9(a2.tree, a2.overlay[0].from + o4), r2.length > l11) return;
        }
      }
      for (let l11 = 0; l11 < s99.children.length; l11++) {
        let h3 = s99.children[l11];
        h3 instanceof E7 && i9(h3, s99.positions[l11] + o4);
      }
    };
    return i9(k11(t5), 0), r2;
  }
  get allowsNesting() {
    return true;
  }
};
d4.setState = v5.define();
function bt6(n22, t5, e4) {
  let r2 = n22.facet(x10), i9 = k11(n22).topNode;
  if (!r2 || r2.allowsNesting) for (let s99 = i9; s99; s99 = s99.enter(t5, e4, w9.ExcludeBuffers | w9.EnterBracketed)) s99.type.isTop && (i9 = s99);
  return i9;
}
function k11(n22) {
  let t5 = n22.field(d4.state, false);
  return t5 ? t5.tree : E7.empty;
}
var tt8 = class {
  constructor(t5) {
    this.doc = t5, this.cursorPos = 0, this.string = "", this.cursor = t5.iter();
  }
  get length() {
    return this.doc.length;
  }
  syncTo(t5) {
    return this.string = this.cursor.next(t5 - this.cursorPos).value, this.cursorPos = t5 + this.string.length, this.cursorPos - this.string.length;
  }
  chunk(t5) {
    return this.syncTo(t5), this.string;
  }
  get lineChunks() {
    return true;
  }
  read(t5, e4) {
    let r2 = this.cursorPos - this.string.length;
    return t5 < r2 || e4 >= this.cursorPos ? this.doc.sliceString(t5, e4) : this.string.slice(t5 - r2, e4 - r2);
  }
};
var I12 = null;
var B12 = class n19 {
  constructor(t5, e4, r2 = [], i9, s99, o4, a2, l11) {
    this.parser = t5, this.state = e4, this.fragments = r2, this.tree = i9, this.treeLen = s99, this.viewport = o4, this.skipped = a2, this.scheduleOn = l11, this.parse = null, this.tempSkipped = [];
  }
  static create(t5, e4, r2) {
    return new n19(t5, e4, [], E7.empty, 0, r2, [], null);
  }
  startParse() {
    return this.parser.startParse(new tt8(this.state.doc), this.fragments);
  }
  work(t5, e4) {
    return e4 != null && e4 >= this.state.doc.length && (e4 = void 0), this.tree != E7.empty && this.isDone(e4 ?? this.state.doc.length) ? (this.takeTree(), true) : this.withContext(() => {
      var r2;
      if (typeof t5 == "number") {
        let i9 = Date.now() + t5;
        t5 = () => Date.now() > i9;
      }
      for (this.parse || (this.parse = this.startParse()), e4 != null && (this.parse.stoppedAt == null || this.parse.stoppedAt > e4) && e4 < this.state.doc.length && this.parse.stopAt(e4); ; ) {
        let i9 = this.parse.advance();
        if (i9) if (this.fragments = this.withoutTempSkipped(re8.addTree(i9, this.fragments, this.parse.stoppedAt != null)), this.treeLen = (r2 = this.parse.stoppedAt) !== null && r2 !== void 0 ? r2 : this.state.doc.length, this.tree = i9, this.parse = null, this.treeLen < (e4 ?? this.state.doc.length)) this.parse = this.startParse();
        else return true;
        if (t5()) return false;
      }
    });
  }
  takeTree() {
    let t5, e4;
    this.parse && (t5 = this.parse.parsedPos) >= this.treeLen && ((this.parse.stoppedAt == null || this.parse.stoppedAt > t5) && this.parse.stopAt(t5), this.withContext(() => {
      for (; !(e4 = this.parse.advance()); ) ;
    }), this.treeLen = t5, this.tree = e4, this.fragments = this.withoutTempSkipped(re8.addTree(this.tree, this.fragments, true)), this.parse = null);
  }
  withContext(t5) {
    let e4 = I12;
    I12 = this;
    try {
      return t5();
    } finally {
      I12 = e4;
    }
  }
  withoutTempSkipped(t5) {
    for (let e4; e4 = this.tempSkipped.pop(); ) t5 = yt6(t5, e4.from, e4.to);
    return t5;
  }
  changes(t5, e4) {
    let { fragments: r2, tree: i9, treeLen: s99, viewport: o4, skipped: a2 } = this;
    if (this.takeTree(), !t5.empty) {
      let l11 = [];
      if (t5.iterChangedRanges((h3, f2, c4, w11) => l11.push({
        fromA: h3,
        toA: f2,
        fromB: c4,
        toB: w11
      })), r2 = re8.applyChanges(r2, l11), i9 = E7.empty, s99 = 0, o4 = {
        from: t5.mapPos(o4.from, -1),
        to: t5.mapPos(o4.to, 1)
      }, this.skipped.length) {
        a2 = [];
        for (let h3 of this.skipped) {
          let f2 = t5.mapPos(h3.from, 1), c4 = t5.mapPos(h3.to, -1);
          f2 < c4 && a2.push({
            from: f2,
            to: c4
          });
        }
      }
    }
    return new n19(this.parser, e4, r2, i9, s99, o4, a2, this.scheduleOn);
  }
  updateViewport(t5) {
    if (this.viewport.from == t5.from && this.viewport.to == t5.to) return false;
    this.viewport = t5;
    let e4 = this.skipped.length;
    for (let r2 = 0; r2 < this.skipped.length; r2++) {
      let { from: i9, to: s99 } = this.skipped[r2];
      i9 < t5.to && s99 > t5.from && (this.fragments = yt6(this.fragments, i9, s99), this.skipped.splice(r2--, 1));
    }
    return this.skipped.length >= e4 ? false : (this.reset(), true);
  }
  reset() {
    this.parse && (this.takeTree(), this.parse = null);
  }
  skipUntilInView(t5, e4) {
    this.skipped.push({
      from: t5,
      to: e4
    });
  }
  static getSkippingParser(t5) {
    return new class extends Ae7 {
      createParse(e4, r2, i9) {
        let s99 = i9[0].from, o4 = i9[i9.length - 1].to;
        return {
          parsedPos: s99,
          advance() {
            let l11 = I12;
            if (l11) {
              for (let h3 of i9) l11.tempSkipped.push(h3);
              t5 && (l11.scheduleOn = l11.scheduleOn ? Promise.all([
                l11.scheduleOn,
                t5
              ]) : t5);
            }
            return this.parsedPos = o4, new E7(M10.none, [], [], o4 - s99);
          },
          stoppedAt: null,
          stopAt() {
          }
        };
      }
    }();
  }
  isDone(t5) {
    t5 = Math.min(t5, this.state.doc.length);
    let e4 = this.fragments;
    return this.treeLen >= t5 && e4.length && e4[0].from == 0 && e4[0].to >= t5;
  }
  static get() {
    return I12;
  }
};
function yt6(n22, t5, e4) {
  return re8.applyChanges(n22, [
    {
      fromA: t5,
      toA: e4,
      fromB: t5,
      toB: e4
    }
  ]);
}
var M12 = class n20 {
  constructor(t5) {
    this.context = t5, this.tree = t5.tree;
  }
  apply(t5) {
    if (!t5.docChanged && this.tree == this.context.tree) return this;
    let e4 = this.context.changes(t5.changes, t5.state), r2 = this.context.treeLen == t5.startState.doc.length ? void 0 : Math.max(t5.changes.mapPos(this.context.treeLen), e4.viewport.to);
    return e4.work(20, r2) || e4.takeTree(), new n20(e4);
  }
  static init(t5) {
    let e4 = Math.min(3e3, t5.doc.length), r2 = B12.create(t5.facet(x10).parser, t5, {
      from: 0,
      to: e4
    });
    return r2.work(20, e4) || r2.takeTree(), new n20(r2);
  }
};
d4.state = z8.define({
  create: M12.init,
  update(n22, t5) {
    for (let e4 of t5.effects) if (e4.is(d4.setState)) return e4.value;
    return t5.startState.facet(x10) != t5.state.facet(x10) ? M12.init(t5.state) : n22.apply(t5);
  }
});
var Ft5 = (n22) => {
  let t5 = setTimeout(() => n22(), 500);
  return () => clearTimeout(t5);
};
typeof requestIdleCallback < "u" && (Ft5 = (n22) => {
  let t5 = -1, e4 = setTimeout(() => {
    t5 = requestIdleCallback(n22, {
      timeout: 400
    });
  }, 100);
  return () => t5 < 0 ? clearTimeout(e4) : cancelIdleCallback(t5);
});
var Y10 = typeof navigator < "u" && (!((X12 = navigator.scheduling) === null || X12 === void 0) && X12.isInputPending) ? () => navigator.scheduling.isInputPending() : null;
var Ut6 = N10.fromClass(class {
  constructor(t5) {
    this.view = t5, this.working = null, this.workScheduled = 0, this.chunkEnd = -1, this.chunkBudget = -1, this.work = this.work.bind(this), this.scheduleWork();
  }
  update(t5) {
    let e4 = this.view.state.field(d4.state).context;
    (e4.updateViewport(t5.view.viewport) || this.view.viewport.to > e4.treeLen) && this.scheduleWork(), (t5.docChanged || t5.selectionSet) && (this.view.hasFocus && (this.chunkBudget += 50), this.scheduleWork()), this.checkAsyncSchedule(e4);
  }
  scheduleWork() {
    if (this.working) return;
    let { state: t5 } = this.view, e4 = t5.field(d4.state);
    (e4.tree != e4.context.tree || !e4.context.isDone(t5.doc.length)) && (this.working = Ft5(this.work));
  }
  work(t5) {
    this.working = null;
    let e4 = Date.now();
    if (this.chunkEnd < e4 && (this.chunkEnd < 0 || this.view.hasFocus) && (this.chunkEnd = e4 + 3e4, this.chunkBudget = 3e3), this.chunkBudget <= 0) return;
    let { state: r2, viewport: { to: i9 } } = this.view, s99 = r2.field(d4.state);
    if (s99.tree == s99.context.tree && s99.context.isDone(i9 + 1e5)) return;
    let o4 = Date.now() + Math.min(this.chunkBudget, 100, t5 && !Y10 ? Math.max(25, t5.timeRemaining() - 5) : 1e9), a2 = s99.context.treeLen < i9 && r2.doc.length > i9 + 1e3, l11 = s99.context.work(() => Y10 && Y10() || Date.now() > o4, i9 + (a2 ? 0 : 1e5));
    this.chunkBudget -= Date.now() - e4, (l11 || this.chunkBudget <= 0) && (s99.context.takeTree(), this.view.dispatch({
      effects: d4.setState.of(new M12(s99.context))
    })), this.chunkBudget > 0 && !(l11 && !a2) && this.scheduleWork(), this.checkAsyncSchedule(s99.context);
  }
  checkAsyncSchedule(t5) {
    t5.scheduleOn && (this.workScheduled++, t5.scheduleOn.then(() => this.scheduleWork()).catch((e4) => U9(this.view.state, e4)).then(() => this.workScheduled--), t5.scheduleOn = null);
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
var x10 = k7.define({
  combine(n22) {
    return n22.length ? n22[0] : null;
  },
  enables: (n22) => [
    d4.state,
    Ut6,
    k8.contentAttributes.compute([
      n22
    ], (t5) => {
      let e4 = t5.facet(n22);
      return e4 && e4.name ? {
        "data-language": e4.name
      } : {};
    })
  ]
});
var me8 = k7.define();
var Wt5 = k7.define({
  combine: (n22) => {
    if (!n22.length) return "  ";
    let t5 = n22[0];
    if (!t5 || /\S/.test(t5) || Array.from(t5).some((e4) => e4 != t5[0])) throw new Error("Invalid indent unit: " + JSON.stringify(n22[0]));
    return t5;
  }
});
var $t5 = new v6();
var Te10 = k7.define();
var Se10 = new v6();
function qt5(n22, t5) {
  let e4 = t5.mapPos(n22.from, 1), r2 = t5.mapPos(n22.to, -1);
  return e4 >= r2 ? void 0 : {
    from: e4,
    to: r2
  };
}
var F11 = v5.define({
  map: qt5
});
var C11 = v5.define({
  map: qt5
});
var T10 = z8.define({
  create() {
    return T8.none;
  },
  update(n22, t5) {
    t5.isUserEvent("delete") && t5.changes.iterChangedRanges((e4, r2) => n22 = Tt7(n22, e4, r2)), n22 = n22.map(t5.changes);
    for (let e4 of t5.effects) if (e4.is(F11) && !Ce10(n22, e4.value.from, e4.value.to)) {
      let { preparePlaceholder: r2 } = t5.state.facet(dt4), i9 = r2 ? T8.replace({
        widget: new nt5(r2(t5.state, e4.value))
      }) : St6;
      n22 = n22.update({
        add: [
          i9.range(e4.value.from, e4.value.to)
        ]
      });
    } else e4.is(C11) && (n22 = n22.update({
      filter: (r2, i9) => e4.value.from != r2 || e4.value.to != i9,
      filterFrom: e4.value.from,
      filterTo: e4.value.to
    }));
    return t5.selection && (n22 = Tt7(n22, t5.selection.main.head)), n22;
  },
  provide: (n22) => k8.decorations.from(n22),
  toJSON(n22, t5) {
    let e4 = [];
    return n22.between(0, t5.doc.length, (r2, i9) => {
      e4.push(r2, i9);
    }), e4;
  },
  fromJSON(n22) {
    if (!Array.isArray(n22) || n22.length % 2) throw new RangeError("Invalid JSON for fold state");
    let t5 = [];
    for (let e4 = 0; e4 < n22.length; ) {
      let r2 = n22[e4++], i9 = n22[e4++];
      if (typeof r2 != "number" || typeof i9 != "number") throw new RangeError("Invalid JSON for fold state");
      t5.push(St6.range(r2, i9));
    }
    return T8.set(t5, true);
  }
});
function Tt7(n22, t5, e4 = t5) {
  let r2 = false;
  return n22.between(t5, e4, (i9, s99) => {
    i9 < e4 && s99 > t5 && (r2 = true);
  }), r2 ? n22.update({
    filterFrom: t5,
    filterTo: e4,
    filter: (i9, s99) => i9 >= e4 || s99 <= t5
  }) : n22;
}
function R11(n22, t5, e4) {
  var r2;
  let i9 = null;
  return (r2 = n22.field(T10, false)) === null || r2 === void 0 || r2.between(t5, e4, (s99, o4) => {
    (!i9 || i9.from > s99) && (i9 = {
      from: s99,
      to: o4
    });
  }), i9;
}
function Ce10(n22, t5, e4) {
  let r2 = false;
  return n22.between(t5, t5, (i9, s99) => {
    i9 == t5 && s99 == e4 && (r2 = true);
  }), r2;
}
var Ne8 = {
  placeholderDOM: null,
  preparePlaceholder: null,
  placeholderText: "\u2026"
};
var dt4 = k7.define({
  combine(n22) {
    return rt4(n22, Ne8);
  }
});
function Jt5(n22, t5) {
  let { state: e4 } = n22, r2 = e4.facet(dt4), i9 = (o4) => {
    let a2 = n22.lineBlockAt(n22.posAtDOM(o4.target)), l11 = R11(n22.state, a2.from, a2.to);
    l11 && n22.dispatch({
      effects: C11.of(l11)
    }), o4.preventDefault();
  };
  if (r2.placeholderDOM) return r2.placeholderDOM(n22, i9, t5);
  let s99 = document.createElement("span");
  return s99.textContent = r2.placeholderText, s99.setAttribute("aria-label", e4.phrase("folded code")), s99.title = e4.phrase("unfold"), s99.className = "cm-foldPlaceholder", s99.onclick = i9, s99;
}
var St6 = T8.replace({
  widget: new class extends et4 {
    toDOM(n22) {
      return Jt5(n22, null);
    }
  }()
});
var nt5 = class extends et4 {
  constructor(t5) {
    super(), this.value = t5;
  }
  eq(t5) {
    return this.value == t5.value;
  }
  toDOM(t5) {
    return Jt5(t5, this.value);
  }
};
var Re9 = k8.baseTheme({
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
var z12 = class n21 {
  constructor(t5, e4) {
    this.specs = t5;
    let r2;
    function i9(a2) {
      let l11 = T2.newName();
      return (r2 || (r2 = /* @__PURE__ */ Object.create(null)))["." + l11] = a2, l11;
    }
    let s99 = typeof e4.all == "string" ? e4.all : e4.all ? i9(e4.all) : void 0, o4 = e4.scope;
    this.scope = o4 instanceof d4 ? (a2) => a2.prop(S9) == o4.data : o4 ? (a2) => a2 == o4 : void 0, this.style = U10(t5.map((a2) => ({
      tag: a2.tag,
      class: a2.class || i9(Object.assign({}, a2, {
        tag: null
      }))
    })), {
      all: s99
    }).style, this.module = r2 ? new T2(r2) : null, this.themeType = e4.themeType;
  }
  static define(t5, e4) {
    return new n21(t5, e4 || {});
  }
};
var rt7 = k7.define();
var _t5 = k7.define({
  combine(n22) {
    return n22.length ? [
      n22[0]
    ] : null;
  }
});
function H9(n22) {
  let t5 = n22.facet(rt7);
  return t5.length ? t5 : n22.facet(_t5);
}
var it8 = class {
  constructor(t5) {
    this.markCache = /* @__PURE__ */ Object.create(null), this.tree = k11(t5.state), this.decorations = this.buildDeco(t5, H9(t5.state)), this.decoratedTo = t5.viewport.to;
  }
  update(t5) {
    let e4 = k11(t5.state), r2 = H9(t5.state), i9 = r2 != H9(t5.startState), { viewport: s99 } = t5.view, o4 = t5.changes.mapPos(this.decoratedTo, 1);
    e4.length < s99.to && !i9 && e4.type == this.tree.type && o4 >= s99.to ? (this.decorations = this.decorations.map(t5.changes), this.decoratedTo = o4) : (e4 != this.tree || t5.viewportChanged || i9) && (this.tree = e4, this.decorations = this.buildDeco(t5.view, r2), this.decoratedTo = s99.to);
  }
  buildDeco(t5, e4) {
    if (!e4 || !this.tree.length) return T8.none;
    let r2 = new re7();
    for (let { from: i9, to: s99 } of t5.visibleRanges) X10(this.tree, e4, (o4, a2, l11) => {
      r2.add(o4, a2, this.markCache[l11] || (this.markCache[l11] = T8.mark({
        class: l11
      })));
    }, i9, s99);
    return r2.finish();
  }
};
var Ee9 = st4.high(N10.fromClass(it8, {
  decorations: (n22) => n22.decorations
}));
var Sn4 = z12.define([
  {
    tag: l10.meta,
    color: "#404740"
  },
  {
    tag: l10.link,
    textDecoration: "underline"
  },
  {
    tag: l10.heading,
    textDecoration: "underline",
    fontWeight: "bold"
  },
  {
    tag: l10.emphasis,
    fontStyle: "italic"
  },
  {
    tag: l10.strong,
    fontWeight: "bold"
  },
  {
    tag: l10.strikethrough,
    textDecoration: "line-through"
  },
  {
    tag: l10.keyword,
    color: "#708"
  },
  {
    tag: [
      l10.atom,
      l10.bool,
      l10.url,
      l10.contentSeparator,
      l10.labelName
    ],
    color: "#219"
  },
  {
    tag: [
      l10.literal,
      l10.inserted
    ],
    color: "#164"
  },
  {
    tag: [
      l10.string,
      l10.deleted
    ],
    color: "#a11"
  },
  {
    tag: [
      l10.regexp,
      l10.escape,
      l10.special(l10.string)
    ],
    color: "#e40"
  },
  {
    tag: l10.definition(l10.variableName),
    color: "#00f"
  },
  {
    tag: l10.local(l10.variableName),
    color: "#30a"
  },
  {
    tag: [
      l10.typeName,
      l10.namespace
    ],
    color: "#085"
  },
  {
    tag: l10.className,
    color: "#167"
  },
  {
    tag: [
      l10.special(l10.variableName),
      l10.macroName
    ],
    color: "#256"
  },
  {
    tag: l10.definition(l10.propertyName),
    color: "#00c"
  },
  {
    tag: l10.comment,
    color: "#940"
  },
  {
    tag: l10.invalid,
    color: "#f00"
  }
]);
var Fe9 = k8.baseTheme({
  "&.cm-focused .cm-matchingBracket": {
    backgroundColor: "#328c8252"
  },
  "&.cm-focused .cm-nonmatchingBracket": {
    backgroundColor: "#bb555544"
  }
});
var Kt5 = 1e4;
var Qt6 = "()[]{}";
var Xt6 = k7.define({
  combine(n22) {
    return rt4(n22, {
      afterCursor: true,
      brackets: Qt6,
      maxScanDistance: Kt5,
      renderMatch: He7
    });
  }
});
var Ue8 = T8.mark({
  class: "cm-matchingBracket"
});
var We8 = T8.mark({
  class: "cm-nonmatchingBracket"
});
function He7(n22) {
  let t5 = [], e4 = n22.matched ? Ue8 : We8;
  return t5.push(e4.range(n22.start.from, n22.start.to)), n22.end && t5.push(e4.range(n22.end.from, n22.end.to)), t5;
}
var Ve7 = z8.define({
  create() {
    return T8.none;
  },
  update(n22, t5) {
    if (!t5.docChanged && !t5.selection) return n22;
    let e4 = [], r2 = t5.state.facet(Xt6);
    for (let i9 of t5.state.selection.ranges) {
      if (!i9.empty) continue;
      let s99 = U12(t5.state, i9.head, -1, r2) || i9.head > 0 && U12(t5.state, i9.head - 1, 1, r2) || r2.afterCursor && (U12(t5.state, i9.head, 1, r2) || i9.head < t5.state.doc.length && U12(t5.state, i9.head + 1, -1, r2));
      s99 && (e4 = e4.concat(r2.renderMatch(s99, t5.state)));
    }
    return T8.set(e4, true);
  },
  provide: (n22) => k8.decorations.from(n22)
});
var je7 = new v6();
function st6(n22, t5, e4) {
  let r2 = n22.prop(t5 < 0 ? v6.openedBy : v6.closedBy);
  if (r2) return r2;
  if (n22.name.length == 1) {
    let i9 = e4.indexOf(n22.name);
    if (i9 > -1 && i9 % 2 == (t5 < 0 ? 1 : 0)) return [
      e4[i9 + t5]
    ];
  }
  return null;
}
function ot7(n22) {
  let t5 = n22.type.prop(je7);
  return t5 ? t5(n22.node) : n22;
}
function U12(n22, t5, e4, r2 = {}) {
  let i9 = r2.maxScanDistance || Kt5, s99 = r2.brackets || Qt6, o4 = k11(n22), a2 = o4.resolveInner(t5, e4);
  for (let l11 = a2; l11; l11 = l11.parent) {
    let h3 = st6(l11.type, e4, s99);
    if (h3 && l11.from < l11.to) {
      let f2 = ot7(l11);
      if (f2 && (e4 > 0 ? t5 >= f2.from && t5 < f2.to : t5 > f2.from && t5 <= f2.to)) return ze9(n22, t5, e4, l11, f2, h3, s99);
    }
  }
  return qe8(n22, t5, e4, o4, a2.type, i9, s99);
}
function ze9(n22, t5, e4, r2, i9, s99, o4) {
  let a2 = r2.parent, l11 = {
    from: i9.from,
    to: i9.to
  }, h3 = 0, f2 = a2?.cursor();
  if (f2 && (e4 < 0 ? f2.childBefore(r2.from) : f2.childAfter(r2.to))) do
    if (e4 < 0 ? f2.to <= r2.from : f2.from >= r2.to) {
      if (h3 == 0 && s99.indexOf(f2.type.name) > -1 && f2.from < f2.to) {
        let c4 = ot7(f2);
        return {
          start: l11,
          end: c4 ? {
            from: c4.from,
            to: c4.to
          } : void 0,
          matched: true
        };
      } else if (st6(f2.type, e4, o4)) h3++;
      else if (st6(f2.type, -e4, o4)) {
        if (h3 == 0) {
          let c4 = ot7(f2);
          return {
            start: l11,
            end: c4 && c4.from < c4.to ? {
              from: c4.from,
              to: c4.to
            } : void 0,
            matched: false
          };
        }
        h3--;
      }
    }
  while (e4 < 0 ? f2.prevSibling() : f2.nextSibling());
  return {
    start: l11,
    matched: false
  };
}
function qe8(n22, t5, e4, r2, i9, s99, o4) {
  let a2 = e4 < 0 ? n22.sliceDoc(t5 - 1, t5) : n22.sliceDoc(t5, t5 + 1), l11 = o4.indexOf(a2);
  if (l11 < 0 || l11 % 2 == 0 != e4 > 0) return null;
  let h3 = {
    from: e4 < 0 ? t5 - 1 : t5,
    to: e4 > 0 ? t5 + 1 : t5
  }, f2 = n22.doc.iterRange(t5, e4 > 0 ? n22.doc.length : 0), c4 = 0;
  for (let w11 = 0; !f2.next().done && w11 <= s99; ) {
    let b9 = f2.value;
    e4 < 0 && (w11 += b9.length);
    let P12 = t5 + w11 * e4;
    for (let A11 = e4 > 0 ? 0 : b9.length - 1, ie10 = e4 > 0 ? b9.length : -1; A11 != ie10; A11 += e4) {
      let Q13 = o4.indexOf(b9[A11]);
      if (!(Q13 < 0 || r2.resolveInner(P12 + A11, 1).type != i9)) if (Q13 % 2 == 0 == e4 > 0) c4++;
      else {
        if (c4 == 1) return {
          start: h3,
          end: {
            from: P12 + A11,
            to: P12 + A11 + 1
          },
          matched: Q13 >> 1 == l11 >> 1
        };
        c4--;
      }
    }
    e4 > 0 && (w11 += b9.length);
  }
  return f2.done ? {
    start: h3,
    matched: false
  } : null;
}
var mt6 = /* @__PURE__ */ Object.create(null);
var E10 = [
  M10.none
];
var Ke7 = new ye8(E10);
var It6 = [];
var Dt6 = /* @__PURE__ */ Object.create(null);
var te11 = /* @__PURE__ */ Object.create(null);
for (let [n22, t5] of [
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
    "tagName"
  ],
  [
    "attribute",
    "attributeName"
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
]) te11[n22] = ee10(mt6, t5);
var G11 = class {
  constructor(t5) {
    this.extra = t5, this.table = Object.assign(/* @__PURE__ */ Object.create(null), te11);
  }
  resolve(t5) {
    return t5 ? this.table[t5] || (this.table[t5] = ee10(this.extra, t5)) : 0;
  }
};
var Qe7 = new G11(mt6);
function Z12(n22, t5) {
  It6.indexOf(n22) > -1 || (It6.push(n22), console.warn(t5));
}
function ee10(n22, t5) {
  let e4 = [];
  for (let a2 of t5.split(" ")) {
    let l11 = [];
    for (let h3 of a2.split(".")) {
      let f2 = n22[h3] || l10[h3];
      f2 ? typeof f2 == "function" ? l11.length ? l11 = l11.map(f2) : Z12(h3, `Modifier ${h3} used at start of tag`) : l11.length ? Z12(h3, `Tag ${h3} used as modifier`) : l11 = Array.isArray(f2) ? f2 : [
        f2
      ] : Z12(h3, `Unknown highlighting tag ${h3}`);
    }
    for (let h3 of l11) e4.push(h3);
  }
  if (!e4.length) return 0;
  let r2 = t5.replace(/ /g, "_"), i9 = r2 + " " + e4.map((a2) => a2.id), s99 = Dt6[i9];
  if (s99) return s99.id;
  let o4 = Dt6[i9] = M10.define({
    id: E10.length,
    name: r2,
    props: [
      _9({
        [r2]: e4
      })
    ]
  });
  return E10.push(o4), o4.id;
}
function ne9(n22) {
  return n22.length <= 4096 && /[\u0590-\u05f4\u0600-\u06ff\u0700-\u08ac\ufb50-\ufdff]/.test(n22);
}
function re9(n22) {
  for (let t5 = n22.iter(); !t5.next().done; ) if (ne9(t5.value)) return true;
  return false;
}
function Ye8(n22) {
  let t5 = false;
  return n22.iterChanges((e4, r2, i9, s99, o4) => {
    !t5 && re9(o4) && (t5 = true);
  }), t5;
}
var at8 = k7.define({
  combine: (n22) => n22.some((t5) => t5)
});
var Ze6 = N10.fromClass(class {
  constructor(n22) {
    this.always = n22.state.facet(at8) || n22.textDirection != R9.LTR || n22.state.facet(k8.perLineTextDirection), this.hasRTL = !this.always && re9(n22.state.doc), this.tree = k11(n22.state), this.decorations = this.always || this.hasRTL ? Ot5(n22, this.tree, this.always) : T8.none;
  }
  update(n22) {
    let t5 = n22.state.facet(at8) || n22.view.textDirection != R9.LTR || n22.state.facet(k8.perLineTextDirection);
    if (!t5 && !this.hasRTL && Ye8(n22.changes) && (this.hasRTL = true), !t5 && !this.hasRTL) return;
    let e4 = k11(n22.state);
    (t5 != this.always || e4 != this.tree || n22.docChanged || n22.viewportChanged) && (this.tree = e4, this.always = t5, this.decorations = Ot5(n22.view, e4, t5));
  }
}, {
  provide: (n22) => {
    function t5(e4) {
      var r2, i9;
      return (i9 = (r2 = e4.plugin(n22)) === null || r2 === void 0 ? void 0 : r2.decorations) !== null && i9 !== void 0 ? i9 : T8.none;
    }
    return [
      k8.outerDecorations.of(t5),
      st4.lowest(k8.bidiIsolatedRanges.of(t5))
    ];
  }
});
function Ot5(n22, t5, e4) {
  let r2 = new re7(), i9 = n22.visibleRanges;
  e4 || (i9 = tn5(i9, n22.state.doc));
  for (let { from: s99, to: o4 } of i9) t5.iterate({
    enter: (a2) => {
      let l11 = a2.type.prop(v6.isolate);
      l11 && r2.add(a2.from, a2.to, en4[l11]);
    },
    from: s99,
    to: o4
  });
  return r2.finish();
}
function tn5(n22, t5) {
  let e4 = t5.iter(), r2 = 0, i9 = [], s99 = null;
  for (let { from: o4, to: a2 } of n22) if (!(s99 && s99.to > o4 && (o4 = s99.to, o4 >= a2))) for (r2 + e4.value.length < o4 && (e4.next(o4 - (r2 + e4.value.length)), r2 = o4); ; ) {
    let l11 = r2, h3 = r2 + e4.value.length;
    if (!e4.lineBreak && ne9(e4.value) && (s99 && s99.to > l11 - 10 ? s99.to = Math.min(a2, h3) : i9.push(s99 = {
      from: l11,
      to: Math.min(a2, h3)
    })), h3 >= a2) break;
    r2 = h3, e4.next();
  }
  return i9;
}
var en4 = {
  rtl: T8.mark({
    class: "cm-iso",
    inclusive: true,
    attributes: {
      dir: "rtl"
    },
    bidiIsolate: R9.RTL
  }),
  ltr: T8.mark({
    class: "cm-iso",
    inclusive: true,
    attributes: {
      dir: "ltr"
    },
    bidiIsolate: R9.LTR
  }),
  auto: T8.mark({
    class: "cm-iso",
    inclusive: true,
    attributes: {
      dir: "auto"
    },
    bidiIsolate: null
  })
};

// deno:https://esm.sh/@codemirror/autocomplete@6.18.4/denonext/autocomplete.mjs
var W11 = class {
  constructor(e4, t5, n22, s99) {
    this.state = e4, this.pos = t5, this.explicit = n22, this.view = s99, this.abortListeners = [], this.abortOnDocChange = false;
  }
  tokenBefore(e4) {
    let t5 = k11(this.state).resolveInner(this.pos, -1);
    for (; t5 && e4.indexOf(t5.name) < 0; ) t5 = t5.parent;
    return t5 ? {
      from: t5.from,
      to: this.pos,
      text: this.state.sliceDoc(t5.from, this.pos),
      type: t5.type
    } : null;
  }
  matchBefore(e4) {
    let t5 = this.state.doc.lineAt(this.pos), n22 = Math.max(t5.from, this.pos - 250), s99 = t5.text.slice(n22 - t5.from, this.pos - t5.from), o4 = s99.search(Le10(e4, false));
    return o4 < 0 ? null : {
      from: n22 + o4,
      to: this.pos,
      text: s99.slice(o4)
    };
  }
  get aborted() {
    return this.abortListeners == null;
  }
  addEventListener(e4, t5, n22) {
    e4 == "abort" && this.abortListeners && (this.abortListeners.push(t5), n22 && n22.onDocChange && (this.abortOnDocChange = true));
  }
};
function me9(i9) {
  let e4 = Object.keys(i9).join(""), t5 = /\w/.test(e4);
  return t5 && (e4 = e4.replace(/\w/g, "")), `[${t5 ? "\\w" : ""}${e4.replace(/[^\w\s]/g, "\\$&")}]`;
}
function Ze7(i9) {
  let e4 = /* @__PURE__ */ Object.create(null), t5 = /* @__PURE__ */ Object.create(null);
  for (let { label: s99 } of i9) {
    e4[s99[0]] = true;
    for (let o4 = 1; o4 < s99.length; o4++) t5[s99[o4]] = true;
  }
  let n22 = me9(e4) + me9(t5) + "*$";
  return [
    new RegExp("^" + n22),
    new RegExp(n22)
  ];
}
function _e9(i9) {
  let e4 = i9.map((s99) => typeof s99 == "string" ? {
    label: s99
  } : s99), [t5, n22] = e4.every((s99) => /^\w+$/.test(s99.label)) ? [
    /\w*$/,
    /\w+$/
  ] : Ze7(e4);
  return (s99) => {
    let o4 = s99.matchBefore(n22);
    return o4 || s99.explicit ? {
      from: o4 ? o4.from : s99.pos,
      options: e4,
      validFor: t5
    } : null;
  };
}
function zt5(i9, e4) {
  return (t5) => {
    for (let n22 = k11(t5.state).resolveInner(t5.pos, -1); n22; n22 = n22.parent) {
      if (i9.indexOf(n22.name) > -1) return e4(t5);
      if (n22.type.isTop) break;
    }
    return null;
  };
}
function Qt7(i9, e4) {
  return (t5) => {
    for (let n22 = k11(t5.state).resolveInner(t5.pos, -1); n22; n22 = n22.parent) {
      if (i9.indexOf(n22.name) > -1) return null;
      if (n22.type.isTop) break;
    }
    return e4(t5);
  };
}
var N13 = class {
  constructor(e4, t5, n22, s99) {
    this.completion = e4, this.source = t5, this.match = n22, this.score = s99;
  }
};
function A10(i9) {
  return i9.selection.main.from;
}
function Le10(i9, e4) {
  var t5;
  let { source: n22 } = i9, s99 = e4 && n22[0] != "^", o4 = n22[n22.length - 1] != "$";
  return !s99 && !o4 ? i9 : new RegExp(`${s99 ? "^" : ""}(?:${n22})${o4 ? "$" : ""}`, (t5 = i9.flags) !== null && t5 !== void 0 ? t5 : i9.ignoreCase ? "i" : "");
}
var ce12 = L7.define();
function et7(i9, e4, t5, n22) {
  let { main: s99 } = i9.selection, o4 = t5 - s99.from, l11 = n22 - s99.from;
  return Object.assign(Object.assign({}, i9.changeByRange((a2) => {
    if (a2 != s99 && t5 != n22 && i9.sliceDoc(a2.from + o4, a2.from + l11) != i9.sliceDoc(t5, n22)) return {
      range: a2
    };
    let r2 = i9.toText(e4);
    return {
      changes: {
        from: a2.from + o4,
        to: n22 == s99.from ? a2.to : a2.from + l11,
        insert: r2
      },
      range: x8.cursor(a2.from + o4 + r2.length)
    };
  })), {
    scrollIntoView: true,
    userEvent: "input.complete"
  });
}
var ge10 = /* @__PURE__ */ new WeakMap();
function tt9(i9) {
  if (!Array.isArray(i9)) return i9;
  let e4 = ge10.get(i9);
  return e4 || ge10.set(i9, e4 = _e9(i9)), e4;
}
var U13 = v5.define();
var M13 = v5.define();
var Z13 = class {
  constructor(e4) {
    this.pattern = e4, this.chars = [], this.folded = [], this.any = [], this.precise = [], this.byWord = [], this.score = 0, this.matched = [];
    for (let t5 = 0; t5 < e4.length; ) {
      let n22 = tt5(e4, t5), s99 = it5(n22);
      this.chars.push(n22);
      let o4 = e4.slice(t5, t5 + s99), l11 = o4.toUpperCase();
      this.folded.push(tt5(l11 == o4 ? o4.toLowerCase() : l11, 0)), t5 += s99;
    }
    this.astral = e4.length != this.chars.length;
  }
  ret(e4, t5) {
    return this.score = e4, this.matched = t5, this;
  }
  match(e4) {
    if (this.pattern.length == 0) return this.ret(-100, []);
    if (e4.length < this.pattern.length) return null;
    let { chars: t5, folded: n22, any: s99, precise: o4, byWord: l11 } = this;
    if (t5.length == 1) {
      let d5 = tt5(e4, 0), D9 = it5(d5), C12 = D9 == e4.length ? 0 : -100;
      if (d5 != t5[0]) if (d5 == n22[0]) C12 += -200;
      else return null;
      return this.ret(C12, [
        0,
        D9
      ]);
    }
    let a2 = e4.indexOf(this.pattern);
    if (a2 == 0) return this.ret(e4.length == this.pattern.length ? 0 : -100, [
      0,
      this.pattern.length
    ]);
    let r2 = t5.length, f2 = 0;
    if (a2 < 0) {
      for (let d5 = 0, D9 = Math.min(e4.length, 200); d5 < D9 && f2 < r2; ) {
        let C12 = tt5(e4, d5);
        (C12 == t5[f2] || C12 == n22[f2]) && (s99[f2++] = d5), d5 += it5(C12);
      }
      if (f2 < r2) return null;
    }
    let c4 = 0, h3 = 0, u5 = false, p5 = 0, b9 = -1, v8 = -1, K10 = /[a-z]/.test(e4), L10 = true;
    for (let d5 = 0, D9 = Math.min(e4.length, 200), C12 = 0; d5 < D9 && h3 < r2; ) {
      let y10 = tt5(e4, d5);
      a2 < 0 && (c4 < r2 && y10 == t5[c4] && (o4[c4++] = d5), p5 < r2 && (y10 == t5[p5] || y10 == n22[p5] ? (p5 == 0 && (b9 = d5), v8 = d5 + 1, p5++) : p5 = 0));
      let $9, z13 = y10 < 255 ? y10 >= 48 && y10 <= 57 || y10 >= 97 && y10 <= 122 ? 2 : y10 >= 65 && y10 <= 90 ? 1 : 0 : ($9 = nt3(y10)) != $9.toLowerCase() ? 1 : $9 != $9.toUpperCase() ? 2 : 0;
      (!d5 || z13 == 1 && K10 || C12 == 0 && z13 != 0) && (t5[h3] == y10 || n22[h3] == y10 && (u5 = true) ? l11[h3++] = d5 : l11.length && (L10 = false)), C12 = z13, d5 += it5(y10);
    }
    return h3 == r2 && l11[0] == 0 && L10 ? this.result(-100 + (u5 ? -200 : 0), l11, e4) : p5 == r2 && b9 == 0 ? this.ret(-200 - e4.length + (v8 == e4.length ? 0 : -100), [
      0,
      v8
    ]) : a2 > -1 ? this.ret(-700 - e4.length, [
      a2,
      a2 + this.pattern.length
    ]) : p5 == r2 ? this.ret(-900 - e4.length, [
      b9,
      v8
    ]) : h3 == r2 ? this.result(-100 + (u5 ? -200 : 0) + -700 + (L10 ? 0 : -1100), l11, e4) : t5.length == 2 ? null : this.result((s99[0] ? -700 : 0) + -200 + -1100, s99, e4);
  }
  result(e4, t5, n22) {
    let s99 = [], o4 = 0;
    for (let l11 of t5) {
      let a2 = l11 + (this.astral ? it5(tt5(n22, l11)) : 1);
      o4 && s99[o4 - 1] == l11 ? s99[o4 - 1] = a2 : (s99[o4++] = l11, s99[o4++] = a2);
    }
    return this.ret(e4 - n22.length, s99);
  }
};
var _10 = class {
  constructor(e4) {
    this.pattern = e4, this.matched = [], this.score = 0, this.folded = e4.toLowerCase();
  }
  match(e4) {
    if (e4.length < this.pattern.length) return null;
    let t5 = e4.slice(0, this.pattern.length), n22 = t5 == this.pattern ? 0 : t5.toLowerCase() == this.folded ? -200 : null;
    return n22 == null ? null : (this.matched = [
      0,
      t5.length
    ], this.score = n22 + (e4.length == this.pattern.length ? 0 : -100), this);
  }
};
var g5 = k7.define({
  combine(i9) {
    return rt4(i9, {
      activateOnTyping: true,
      activateOnCompletion: () => false,
      activateOnTypingDelay: 100,
      selectOnOpen: true,
      override: null,
      closeOnBlur: true,
      maxRenderedOptions: 100,
      defaultKeymap: true,
      tooltipClass: () => "",
      optionClass: () => "",
      aboveCursor: false,
      icons: true,
      addToOptions: [],
      positionInfo: it9,
      filterStrict: false,
      compareCompletions: (e4, t5) => e4.label.localeCompare(t5.label),
      interactionDelay: 75,
      updateSyncTime: 100
    }, {
      defaultKeymap: (e4, t5) => e4 && t5,
      closeOnBlur: (e4, t5) => e4 && t5,
      icons: (e4, t5) => e4 && t5,
      tooltipClass: (e4, t5) => (n22) => be9(e4(n22), t5(n22)),
      optionClass: (e4, t5) => (n22) => be9(e4(n22), t5(n22)),
      addToOptions: (e4, t5) => e4.concat(t5),
      filterStrict: (e4, t5) => e4 || t5
    });
  }
});
function be9(i9, e4) {
  return i9 ? e4 ? i9 + " " + e4 : i9 : e4;
}
function it9(i9, e4, t5, n22, s99, o4) {
  let l11 = i9.textDirection == R9.RTL, a2 = l11, r2 = false, f2 = "top", c4, h3, u5 = e4.left - s99.left, p5 = s99.right - e4.right, b9 = n22.right - n22.left, v8 = n22.bottom - n22.top;
  if (a2 && u5 < Math.min(b9, p5) ? a2 = false : !a2 && p5 < Math.min(b9, u5) && (a2 = true), b9 <= (a2 ? u5 : p5)) c4 = Math.max(s99.top, Math.min(t5.top, s99.bottom - v8)) - e4.top, h3 = Math.min(400, a2 ? u5 : p5);
  else {
    r2 = true, h3 = Math.min(400, (l11 ? e4.right : s99.right - e4.left) - 30);
    let d5 = s99.bottom - e4.bottom;
    d5 >= v8 || d5 > e4.top ? c4 = t5.bottom - e4.top : (f2 = "bottom", c4 = e4.bottom - t5.top);
  }
  let K10 = (e4.bottom - e4.top) / o4.offsetHeight, L10 = (e4.right - e4.left) / o4.offsetWidth;
  return {
    style: `${f2}: ${c4 / K10}px; max-width: ${h3 / L10}px`,
    class: "cm-completionInfo-" + (r2 ? l11 ? "left-narrow" : "right-narrow" : a2 ? "left" : "right")
  };
}
function nt6(i9) {
  let e4 = i9.addToOptions.slice();
  return i9.icons && e4.push({
    render(t5) {
      let n22 = document.createElement("div");
      return n22.classList.add("cm-completionIcon"), t5.type && n22.classList.add(...t5.type.split(/\s+/g).map((s99) => "cm-completionIcon-" + s99)), n22.setAttribute("aria-hidden", "true"), n22;
    },
    position: 20
  }), e4.push({
    render(t5, n22, s99, o4) {
      let l11 = document.createElement("span");
      l11.className = "cm-completionLabel";
      let a2 = t5.displayLabel || t5.label, r2 = 0;
      for (let f2 = 0; f2 < o4.length; ) {
        let c4 = o4[f2++], h3 = o4[f2++];
        c4 > r2 && l11.appendChild(document.createTextNode(a2.slice(r2, c4)));
        let u5 = l11.appendChild(document.createElement("span"));
        u5.appendChild(document.createTextNode(a2.slice(c4, h3))), u5.className = "cm-completionMatchedText", r2 = h3;
      }
      return r2 < a2.length && l11.appendChild(document.createTextNode(a2.slice(r2))), l11;
    },
    position: 50
  }, {
    render(t5) {
      if (!t5.detail) return null;
      let n22 = document.createElement("span");
      return n22.className = "cm-completionDetail", n22.textContent = t5.detail, n22;
    },
    position: 80
  }), e4.sort((t5, n22) => t5.position - n22.position).map((t5) => t5.render);
}
function Q12(i9, e4, t5) {
  if (i9 <= t5) return {
    from: 0,
    to: i9
  };
  if (e4 < 0 && (e4 = 0), e4 <= i9 >> 1) {
    let s99 = Math.floor(e4 / t5);
    return {
      from: s99 * t5,
      to: (s99 + 1) * t5
    };
  }
  let n22 = Math.floor((i9 - e4) / t5);
  return {
    from: i9 - (n22 + 1) * t5,
    to: i9 - n22 * t5
  };
}
var ee11 = class {
  constructor(e4, t5, n22) {
    this.view = e4, this.stateField = t5, this.applyCompletion = n22, this.info = null, this.infoDestroy = null, this.placeInfoReq = {
      read: () => this.measureInfo(),
      write: (r2) => this.placeInfo(r2),
      key: this
    }, this.space = null, this.currentClass = "";
    let s99 = e4.state.field(t5), { options: o4, selected: l11 } = s99.open, a2 = e4.state.facet(g5);
    this.optionContent = nt6(a2), this.optionClass = a2.optionClass, this.tooltipClass = a2.tooltipClass, this.range = Q12(o4.length, l11, a2.maxRenderedOptions), this.dom = document.createElement("div"), this.dom.className = "cm-tooltip-autocomplete", this.updateTooltipClass(e4.state), this.dom.addEventListener("mousedown", (r2) => {
      let { options: f2 } = e4.state.field(t5).open;
      for (let c4 = r2.target, h3; c4 && c4 != this.dom; c4 = c4.parentNode) if (c4.nodeName == "LI" && (h3 = /-(\d+)$/.exec(c4.id)) && +h3[1] < f2.length) {
        this.applyCompletion(e4, f2[+h3[1]]), r2.preventDefault();
        return;
      }
    }), this.dom.addEventListener("focusout", (r2) => {
      let f2 = e4.state.field(this.stateField, false);
      f2 && f2.tooltip && e4.state.facet(g5).closeOnBlur && r2.relatedTarget != e4.contentDOM && e4.dispatch({
        effects: M13.of(null)
      });
    }), this.showOptions(o4, s99.id);
  }
  mount() {
    this.updateSel();
  }
  showOptions(e4, t5) {
    this.list && this.list.remove(), this.list = this.dom.appendChild(this.createListBox(e4, t5, this.range)), this.list.addEventListener("scroll", () => {
      this.info && this.view.requestMeasure(this.placeInfoReq);
    });
  }
  update(e4) {
    var t5;
    let n22 = e4.state.field(this.stateField), s99 = e4.startState.field(this.stateField);
    if (this.updateTooltipClass(e4.state), n22 != s99) {
      let { options: o4, selected: l11, disabled: a2 } = n22.open;
      (!s99.open || s99.open.options != o4) && (this.range = Q12(o4.length, l11, e4.state.facet(g5).maxRenderedOptions), this.showOptions(o4, n22.id)), this.updateSel(), a2 != ((t5 = s99.open) === null || t5 === void 0 ? void 0 : t5.disabled) && this.dom.classList.toggle("cm-tooltip-autocomplete-disabled", !!a2);
    }
  }
  updateTooltipClass(e4) {
    let t5 = this.tooltipClass(e4);
    if (t5 != this.currentClass) {
      for (let n22 of this.currentClass.split(" ")) n22 && this.dom.classList.remove(n22);
      for (let n22 of t5.split(" ")) n22 && this.dom.classList.add(n22);
      this.currentClass = t5;
    }
  }
  positioned(e4) {
    this.space = e4, this.info && this.view.requestMeasure(this.placeInfoReq);
  }
  updateSel() {
    let e4 = this.view.state.field(this.stateField), t5 = e4.open;
    if ((t5.selected > -1 && t5.selected < this.range.from || t5.selected >= this.range.to) && (this.range = Q12(t5.options.length, t5.selected, this.view.state.facet(g5).maxRenderedOptions), this.showOptions(t5.options, e4.id)), this.updateSelectedOption(t5.selected)) {
      this.destroyInfo();
      let { completion: n22 } = t5.options[t5.selected], { info: s99 } = n22;
      if (!s99) return;
      let o4 = typeof s99 == "string" ? document.createTextNode(s99) : s99(n22);
      if (!o4) return;
      "then" in o4 ? o4.then((l11) => {
        l11 && this.view.state.field(this.stateField, false) == e4 && this.addInfoPane(l11, n22);
      }).catch((l11) => U9(this.view.state, l11, "completion info")) : this.addInfoPane(o4, n22);
    }
  }
  addInfoPane(e4, t5) {
    this.destroyInfo();
    let n22 = this.info = document.createElement("div");
    if (n22.className = "cm-tooltip cm-completionInfo", e4.nodeType != null) n22.appendChild(e4), this.infoDestroy = null;
    else {
      let { dom: s99, destroy: o4 } = e4;
      n22.appendChild(s99), this.infoDestroy = o4 || null;
    }
    this.dom.appendChild(n22), this.view.requestMeasure(this.placeInfoReq);
  }
  updateSelectedOption(e4) {
    let t5 = null;
    for (let n22 = this.list.firstChild, s99 = this.range.from; n22; n22 = n22.nextSibling, s99++) n22.nodeName != "LI" || !n22.id ? s99-- : s99 == e4 ? n22.hasAttribute("aria-selected") || (n22.setAttribute("aria-selected", "true"), t5 = n22) : n22.hasAttribute("aria-selected") && n22.removeAttribute("aria-selected");
    return t5 && ot8(this.list, t5), t5;
  }
  measureInfo() {
    let e4 = this.dom.querySelector("[aria-selected]");
    if (!e4 || !this.info) return null;
    let t5 = this.dom.getBoundingClientRect(), n22 = this.info.getBoundingClientRect(), s99 = e4.getBoundingClientRect(), o4 = this.space;
    if (!o4) {
      let l11 = this.dom.ownerDocument.defaultView || globalThis;
      o4 = {
        left: 0,
        top: 0,
        right: l11.innerWidth,
        bottom: l11.innerHeight
      };
    }
    return s99.top > Math.min(o4.bottom, t5.bottom) - 10 || s99.bottom < Math.max(o4.top, t5.top) + 10 ? null : this.view.state.facet(g5).positionInfo(this.view, t5, s99, n22, o4, this.dom);
  }
  placeInfo(e4) {
    this.info && (e4 ? (e4.style && (this.info.style.cssText = e4.style), this.info.className = "cm-tooltip cm-completionInfo " + (e4.class || "")) : this.info.style.cssText = "top: -1e6px");
  }
  createListBox(e4, t5, n22) {
    let s99 = document.createElement("ul");
    s99.id = t5, s99.setAttribute("role", "listbox"), s99.setAttribute("aria-expanded", "true"), s99.setAttribute("aria-label", this.view.state.phrase("Completions"));
    let o4 = null;
    for (let l11 = n22.from; l11 < n22.to; l11++) {
      let { completion: a2, match: r2 } = e4[l11], { section: f2 } = a2;
      if (f2) {
        let u5 = typeof f2 == "string" ? f2 : f2.name;
        if (u5 != o4 && (l11 > n22.from || n22.from == 0)) if (o4 = u5, typeof f2 != "string" && f2.header) s99.appendChild(f2.header(f2));
        else {
          let p5 = s99.appendChild(document.createElement("completion-section"));
          p5.textContent = u5;
        }
      }
      let c4 = s99.appendChild(document.createElement("li"));
      c4.id = t5 + "-" + l11, c4.setAttribute("role", "option");
      let h3 = this.optionClass(a2);
      h3 && (c4.className = h3);
      for (let u5 of this.optionContent) {
        let p5 = u5(a2, this.view.state, this.view, r2);
        p5 && c4.appendChild(p5);
      }
    }
    return n22.from && s99.classList.add("cm-completionListIncompleteTop"), n22.to < e4.length && s99.classList.add("cm-completionListIncompleteBottom"), s99;
  }
  destroyInfo() {
    this.info && (this.infoDestroy && this.infoDestroy(), this.info.remove(), this.info = null);
  }
  destroy() {
    this.destroyInfo();
  }
};
function st7(i9, e4) {
  return (t5) => new ee11(t5, i9, e4);
}
function ot8(i9, e4) {
  let t5 = i9.getBoundingClientRect(), n22 = e4.getBoundingClientRect(), s99 = t5.height / i9.offsetHeight;
  n22.top < t5.top ? i9.scrollTop -= (t5.top - n22.top) / s99 : n22.bottom > t5.bottom && (i9.scrollTop += (n22.bottom - t5.bottom) / s99);
}
function ye10(i9) {
  return (i9.boost || 0) * 100 + (i9.apply ? 10 : 0) + (i9.info ? 5 : 0) + (i9.type ? 1 : 0);
}
function lt6(i9, e4) {
  let t5 = [], n22 = null, s99 = (f2) => {
    t5.push(f2);
    let { section: c4 } = f2.completion;
    if (c4) {
      n22 || (n22 = []);
      let h3 = typeof c4 == "string" ? c4 : c4.name;
      n22.some((u5) => u5.name == h3) || n22.push(typeof c4 == "string" ? {
        name: h3
      } : c4);
    }
  }, o4 = e4.facet(g5);
  for (let f2 of i9) if (f2.hasResult()) {
    let c4 = f2.result.getMatch;
    if (f2.result.filter === false) for (let h3 of f2.result.options) s99(new N13(h3, f2.source, c4 ? c4(h3) : [], 1e9 - t5.length));
    else {
      let h3 = e4.sliceDoc(f2.from, f2.to), u5, p5 = o4.filterStrict ? new _10(h3) : new Z13(h3);
      for (let b9 of f2.result.options) if (u5 = p5.match(b9.label)) {
        let v8 = b9.displayLabel ? c4 ? c4(b9, u5.matched) : [] : u5.matched;
        s99(new N13(b9, f2.source, v8, u5.score + (b9.boost || 0)));
      }
    }
  }
  if (n22) {
    let f2 = /* @__PURE__ */ Object.create(null), c4 = 0, h3 = (u5, p5) => {
      var b9, v8;
      return ((b9 = u5.rank) !== null && b9 !== void 0 ? b9 : 1e9) - ((v8 = p5.rank) !== null && v8 !== void 0 ? v8 : 1e9) || (u5.name < p5.name ? -1 : 1);
    };
    for (let u5 of n22.sort(h3)) c4 -= 1e5, f2[u5.name] = c4;
    for (let u5 of t5) {
      let { section: p5 } = u5.completion;
      p5 && (u5.score += f2[typeof p5 == "string" ? p5 : p5.name]);
    }
  }
  let l11 = [], a2 = null, r2 = o4.compareCompletions;
  for (let f2 of t5.sort((c4, h3) => h3.score - c4.score || r2(c4.completion, h3.completion))) {
    let c4 = f2.completion;
    !a2 || a2.label != c4.label || a2.detail != c4.detail || a2.type != null && c4.type != null && a2.type != c4.type || a2.apply != c4.apply || a2.boost != c4.boost ? l11.push(f2) : ye10(f2.completion) > ye10(a2) && (l11[l11.length - 1] = f2), a2 = f2.completion;
  }
  return l11;
}
var te12 = class i2 {
  constructor(e4, t5, n22, s99, o4, l11) {
    this.options = e4, this.attrs = t5, this.tooltip = n22, this.timestamp = s99, this.selected = o4, this.disabled = l11;
  }
  setSelected(e4, t5) {
    return e4 == this.selected || e4 >= this.options.length ? this : new i2(this.options, ve10(t5, e4), this.tooltip, this.timestamp, e4, this.disabled);
  }
  static build(e4, t5, n22, s99, o4, l11) {
    if (s99 && !l11 && e4.some((f2) => f2.isPending)) return s99.setDisabled();
    let a2 = lt6(e4, t5);
    if (!a2.length) return s99 && e4.some((f2) => f2.isPending) ? s99.setDisabled() : null;
    let r2 = t5.facet(g5).selectOnOpen ? 0 : -1;
    if (s99 && s99.selected != r2 && s99.selected != -1) {
      let f2 = s99.options[s99.selected].completion;
      for (let c4 = 0; c4 < a2.length; c4++) if (a2[c4].completion == f2) {
        r2 = c4;
        break;
      }
    }
    return new i2(a2, ve10(n22, r2), {
      pos: e4.reduce((f2, c4) => c4.hasResult() ? Math.min(f2, c4.from) : f2, 1e8),
      create: ut4,
      above: o4.aboveCursor
    }, s99 ? s99.timestamp : Date.now(), r2, false);
  }
  map(e4) {
    return new i2(this.options, this.attrs, Object.assign(Object.assign({}, this.tooltip), {
      pos: e4.mapPos(this.tooltip.pos)
    }), this.timestamp, this.selected, this.disabled);
  }
  setDisabled() {
    return new i2(this.options, this.attrs, this.tooltip, this.timestamp, this.selected, true);
  }
};
var ie9 = class i3 {
  constructor(e4, t5, n22) {
    this.active = e4, this.id = t5, this.open = n22;
  }
  static start() {
    return new i3(ft6, "cm-ac-" + Math.floor(Math.random() * 2e6).toString(36), null);
  }
  update(e4) {
    let { state: t5 } = e4, n22 = t5.facet(g5), o4 = (n22.override || t5.languageDataAt("autocomplete", A10(t5)).map(tt9)).map((r2) => (this.active.find((c4) => c4.source == r2) || new S10(r2, this.active.some((c4) => c4.state != 0) ? 1 : 0)).update(e4, n22));
    o4.length == this.active.length && o4.every((r2, f2) => r2 == this.active[f2]) && (o4 = this.active);
    let l11 = this.open, a2 = e4.effects.some((r2) => r2.is(fe9));
    l11 && e4.docChanged && (l11 = l11.map(e4.changes)), e4.selection || o4.some((r2) => r2.hasResult() && e4.changes.touchesRange(r2.from, r2.to)) || !rt8(o4, this.active) || a2 ? l11 = te12.build(o4, t5, this.id, l11, n22, a2) : l11 && l11.disabled && !o4.some((r2) => r2.isPending) && (l11 = null), !l11 && o4.every((r2) => !r2.isPending) && o4.some((r2) => r2.hasResult()) && (o4 = o4.map((r2) => r2.hasResult() ? new S10(r2.source, 0) : r2));
    for (let r2 of e4.effects) r2.is(he9) && (l11 = l11 && l11.setSelected(r2.value, this.id));
    return o4 == this.active && l11 == this.open ? this : new i3(o4, this.id, l11);
  }
  get tooltip() {
    return this.open ? this.open.tooltip : null;
  }
  get attrs() {
    return this.open ? this.open.attrs : this.active.length ? at9 : ct6;
  }
};
function rt8(i9, e4) {
  if (i9 == e4) return true;
  for (let t5 = 0, n22 = 0; ; ) {
    for (; t5 < i9.length && !i9[t5].hasResult(); ) t5++;
    for (; n22 < e4.length && !e4[n22].hasResult(); ) n22++;
    let s99 = t5 == i9.length, o4 = n22 == e4.length;
    if (s99 || o4) return s99 == o4;
    if (i9[t5++].result != e4[n22++].result) return false;
  }
}
var at9 = {
  "aria-autocomplete": "list"
};
var ct6 = {};
function ve10(i9, e4) {
  let t5 = {
    "aria-autocomplete": "list",
    "aria-haspopup": "listbox",
    "aria-controls": i9
  };
  return e4 > -1 && (t5["aria-activedescendant"] = i9 + "-" + e4), t5;
}
var ft6 = [];
function Me9(i9, e4) {
  if (i9.isUserEvent("input.complete")) {
    let n22 = i9.annotation(ce12);
    if (n22 && e4.activateOnCompletion(n22)) return 12;
  }
  let t5 = i9.isUserEvent("input.type");
  return t5 && e4.activateOnTyping ? 5 : t5 ? 1 : i9.isUserEvent("delete.backward") ? 2 : i9.selection ? 8 : i9.docChanged ? 16 : 0;
}
var S10 = class i4 {
  constructor(e4, t5, n22 = false) {
    this.source = e4, this.state = t5, this.explicit = n22;
  }
  hasResult() {
    return false;
  }
  get isPending() {
    return this.state == 1;
  }
  update(e4, t5) {
    let n22 = Me9(e4, t5), s99 = this;
    (n22 & 8 || n22 & 16 && this.touches(e4)) && (s99 = new i4(s99.source, 0)), n22 & 4 && s99.state == 0 && (s99 = new i4(this.source, 1)), s99 = s99.updateFor(e4, n22);
    for (let o4 of e4.effects) if (o4.is(U13)) s99 = new i4(s99.source, 1, o4.value);
    else if (o4.is(M13)) s99 = new i4(s99.source, 0);
    else if (o4.is(fe9)) for (let l11 of o4.value) l11.source == s99.source && (s99 = l11);
    return s99;
  }
  updateFor(e4, t5) {
    return this.map(e4.changes);
  }
  map(e4) {
    return this;
  }
  touches(e4) {
    return e4.changes.touchesRange(A10(e4.state));
  }
};
var V12 = class i5 extends S10 {
  constructor(e4, t5, n22, s99, o4, l11) {
    super(e4, 3, t5), this.limit = n22, this.result = s99, this.from = o4, this.to = l11;
  }
  hasResult() {
    return true;
  }
  updateFor(e4, t5) {
    var n22;
    if (!(t5 & 3)) return this.map(e4.changes);
    let s99 = this.result;
    s99.map && !e4.changes.empty && (s99 = s99.map(s99, e4.changes));
    let o4 = e4.changes.mapPos(this.from), l11 = e4.changes.mapPos(this.to, 1), a2 = A10(e4.state);
    if (a2 > l11 || !s99 || t5 & 2 && (A10(e4.startState) == this.from || a2 < this.limit)) return new S10(this.source, t5 & 4 ? 1 : 0);
    let r2 = e4.changes.mapPos(this.limit);
    return ht7(s99.validFor, e4.state, o4, l11) ? new i5(this.source, this.explicit, r2, s99, o4, l11) : s99.update && (s99 = s99.update(s99, o4, l11, new W11(e4.state, a2, false))) ? new i5(this.source, this.explicit, r2, s99, s99.from, (n22 = s99.to) !== null && n22 !== void 0 ? n22 : A10(e4.state)) : new S10(this.source, 1, this.explicit);
  }
  map(e4) {
    return e4.empty ? this : (this.result.map ? this.result.map(this.result, e4) : this.result) ? new i5(this.source, this.explicit, e4.mapPos(this.limit), this.result, e4.mapPos(this.from), e4.mapPos(this.to, 1)) : new S10(this.source, 0);
  }
  touches(e4) {
    return e4.changes.touchesRange(this.from, this.to);
  }
};
function ht7(i9, e4, t5, n22) {
  if (!i9) return false;
  let s99 = e4.sliceDoc(t5, n22);
  return typeof i9 == "function" ? i9(s99, t5, n22, e4) : Le10(i9, true).test(s99);
}
var fe9 = v5.define({
  map(i9, e4) {
    return i9.map((t5) => t5.map(e4));
  }
});
var he9 = v5.define();
var m8 = z8.define({
  create() {
    return ie9.start();
  },
  update(i9, e4) {
    return i9.update(e4);
  },
  provide: (i9) => [
    $n2.from(i9, (e4) => e4.tooltip),
    k8.contentAttributes.from(i9, (e4) => e4.attrs)
  ]
});
function ue9(i9, e4) {
  let t5 = e4.completion.apply || e4.completion.label, n22 = i9.state.field(m8).active.find((s99) => s99.source == e4.source);
  return n22 instanceof V12 ? (typeof t5 == "string" ? i9.dispatch(Object.assign(Object.assign({}, et7(i9.state, t5, n22.from, n22.to)), {
    annotations: ce12.of(e4.completion)
  })) : t5(i9, e4.completion, n22.from, n22.to), true) : false;
}
var ut4 = st7(m8, ue9);
function F12(i9, e4 = "option") {
  return (t5) => {
    let n22 = t5.state.field(m8, false);
    if (!n22 || !n22.open || n22.open.disabled || Date.now() - n22.open.timestamp < t5.state.facet(g5).interactionDelay) return false;
    let s99 = 1, o4;
    e4 == "page" && (o4 = Bl(t5, n22.open.tooltip)) && (s99 = Math.max(2, Math.floor(o4.dom.offsetHeight / o4.dom.querySelector("li").offsetHeight) - 1));
    let { length: l11 } = n22.open.options, a2 = n22.open.selected > -1 ? n22.open.selected + s99 * (i9 ? 1 : -1) : i9 ? 0 : l11 - 1;
    return a2 < 0 ? a2 = e4 == "page" ? 0 : l11 - 1 : a2 >= l11 && (a2 = e4 == "page" ? l11 - 1 : 0), t5.dispatch({
      effects: he9.of(a2)
    }), true;
  };
}
var pt6 = (i9) => {
  let e4 = i9.state.field(m8, false);
  return i9.state.readOnly || !e4 || !e4.open || e4.open.selected < 0 || e4.open.disabled || Date.now() - e4.open.timestamp < i9.state.facet(g5).interactionDelay ? false : ue9(i9, e4.open.options[e4.open.selected]);
};
var xe11 = (i9) => i9.state.field(m8, false) ? (i9.dispatch({
  effects: U13.of(true)
}), true) : false;
var dt5 = (i9) => {
  let e4 = i9.state.field(m8, false);
  return !e4 || !e4.active.some((t5) => t5.state != 0) ? false : (i9.dispatch({
    effects: M13.of(null)
  }), true);
};
var ne10 = class {
  constructor(e4, t5) {
    this.active = e4, this.context = t5, this.time = Date.now(), this.updates = [], this.done = void 0;
  }
};
var mt7 = 50;
var gt4 = 1e3;
var bt7 = N10.fromClass(class {
  constructor(i9) {
    this.view = i9, this.debounceUpdate = -1, this.running = [], this.debounceAccept = -1, this.pendingStart = false, this.composing = 0;
    for (let e4 of i9.state.field(m8).active) e4.isPending && this.startQuery(e4);
  }
  update(i9) {
    let e4 = i9.state.field(m8), t5 = i9.state.facet(g5);
    if (!i9.selectionSet && !i9.docChanged && i9.startState.field(m8) == e4) return;
    let n22 = i9.transactions.some((o4) => {
      let l11 = Me9(o4, t5);
      return l11 & 8 || (o4.selection || o4.docChanged) && !(l11 & 3);
    });
    for (let o4 = 0; o4 < this.running.length; o4++) {
      let l11 = this.running[o4];
      if (n22 || l11.context.abortOnDocChange && i9.docChanged || l11.updates.length + i9.transactions.length > mt7 && Date.now() - l11.time > gt4) {
        for (let a2 of l11.context.abortListeners) try {
          a2();
        } catch (r2) {
          U9(this.view.state, r2);
        }
        l11.context.abortListeners = null, this.running.splice(o4--, 1);
      } else l11.updates.push(...i9.transactions);
    }
    this.debounceUpdate > -1 && clearTimeout(this.debounceUpdate), i9.transactions.some((o4) => o4.effects.some((l11) => l11.is(U13))) && (this.pendingStart = true);
    let s99 = this.pendingStart ? 50 : t5.activateOnTypingDelay;
    if (this.debounceUpdate = e4.active.some((o4) => o4.isPending && !this.running.some((l11) => l11.active.source == o4.source)) ? setTimeout(() => this.startUpdate(), s99) : -1, this.composing != 0) for (let o4 of i9.transactions) o4.isUserEvent("input.type") ? this.composing = 2 : this.composing == 2 && o4.selection && (this.composing = 3);
  }
  startUpdate() {
    this.debounceUpdate = -1, this.pendingStart = false;
    let { state: i9 } = this.view, e4 = i9.field(m8);
    for (let t5 of e4.active) t5.isPending && !this.running.some((n22) => n22.active.source == t5.source) && this.startQuery(t5);
    this.running.length && e4.open && e4.open.disabled && (this.debounceAccept = setTimeout(() => this.accept(), this.view.state.facet(g5).updateSyncTime));
  }
  startQuery(i9) {
    let { state: e4 } = this.view, t5 = A10(e4), n22 = new W11(e4, t5, i9.explicit, this.view), s99 = new ne10(i9, n22);
    this.running.push(s99), Promise.resolve(i9.source(n22)).then((o4) => {
      s99.context.aborted || (s99.done = o4 || null, this.scheduleAccept());
    }, (o4) => {
      this.view.dispatch({
        effects: M13.of(null)
      }), U9(this.view.state, o4);
    });
  }
  scheduleAccept() {
    this.running.every((i9) => i9.done !== void 0) ? this.accept() : this.debounceAccept < 0 && (this.debounceAccept = setTimeout(() => this.accept(), this.view.state.facet(g5).updateSyncTime));
  }
  accept() {
    var i9;
    this.debounceAccept > -1 && clearTimeout(this.debounceAccept), this.debounceAccept = -1;
    let e4 = [], t5 = this.view.state.facet(g5), n22 = this.view.state.field(m8);
    for (let s99 = 0; s99 < this.running.length; s99++) {
      let o4 = this.running[s99];
      if (o4.done === void 0) continue;
      if (this.running.splice(s99--, 1), o4.done) {
        let a2 = A10(o4.updates.length ? o4.updates[0].startState : this.view.state), r2 = Math.min(a2, o4.done.from + (o4.active.explicit ? 0 : 1)), f2 = new V12(o4.active.source, o4.active.explicit, r2, o4.done, o4.done.from, (i9 = o4.done.to) !== null && i9 !== void 0 ? i9 : a2);
        for (let c4 of o4.updates) f2 = f2.update(c4, t5);
        if (f2.hasResult()) {
          e4.push(f2);
          continue;
        }
      }
      let l11 = n22.active.find((a2) => a2.source == o4.active.source);
      if (l11 && l11.isPending) if (o4.done == null) {
        let a2 = new S10(o4.active.source, 0);
        for (let r2 of o4.updates) a2 = a2.update(r2, t5);
        a2.isPending || e4.push(a2);
      } else this.startQuery(l11);
    }
    (e4.length || n22.open && n22.open.disabled) && this.view.dispatch({
      effects: fe9.of(e4)
    });
  }
}, {
  eventHandlers: {
    blur(i9) {
      let e4 = this.view.state.field(m8, false);
      if (e4 && e4.tooltip && this.view.state.facet(g5).closeOnBlur) {
        let t5 = e4.open && Bl(this.view, e4.open.tooltip);
        (!t5 || !t5.dom.contains(i9.relatedTarget)) && setTimeout(() => this.view.dispatch({
          effects: M13.of(null)
        }), 10);
      }
    },
    compositionstart() {
      this.composing = 1;
    },
    compositionend() {
      this.composing == 3 && setTimeout(() => this.view.dispatch({
        effects: U13.of(false)
      }), 20), this.composing = 0;
    }
  }
});
var yt7 = typeof navigator == "object" && /Win/.test(navigator.platform);
var vt5 = st4.highest(k8.domEventHandlers({
  keydown(i9, e4) {
    let t5 = e4.state.field(m8, false);
    if (!t5 || !t5.open || t5.open.disabled || t5.open.selected < 0 || i9.key.length > 1 || i9.ctrlKey && !(yt7 && i9.altKey) || i9.metaKey) return false;
    let n22 = t5.open.options[t5.open.selected], s99 = t5.active.find((l11) => l11.source == n22.source), o4 = n22.completion.commitCharacters || s99.result.commitCharacters;
    return o4 && o4.indexOf(i9.key) > -1 && ue9(e4, n22), false;
  }
}));
var ke10 = k8.baseTheme({
  ".cm-tooltip.cm-tooltip-autocomplete": {
    "& > ul": {
      fontFamily: "monospace",
      whiteSpace: "nowrap",
      overflow: "hidden auto",
      maxWidth_fallback: "700px",
      maxWidth: "min(700px, 95vw)",
      minWidth: "250px",
      maxHeight: "10em",
      height: "100%",
      listStyle: "none",
      margin: 0,
      padding: 0,
      "& > li, & > completion-section": {
        padding: "1px 3px",
        lineHeight: 1.2
      },
      "& > li": {
        overflowX: "hidden",
        textOverflow: "ellipsis",
        cursor: "pointer"
      },
      "& > completion-section": {
        display: "list-item",
        borderBottom: "1px solid silver",
        paddingLeft: "0.5em",
        opacity: 0.7
      }
    }
  },
  "&light .cm-tooltip-autocomplete ul li[aria-selected]": {
    background: "#17c",
    color: "white"
  },
  "&light .cm-tooltip-autocomplete-disabled ul li[aria-selected]": {
    background: "#777"
  },
  "&dark .cm-tooltip-autocomplete ul li[aria-selected]": {
    background: "#347",
    color: "white"
  },
  "&dark .cm-tooltip-autocomplete-disabled ul li[aria-selected]": {
    background: "#444"
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
    maxWidth: "400px",
    boxSizing: "border-box",
    whiteSpace: "pre-line"
  },
  ".cm-completionInfo.cm-completionInfo-left": {
    right: "100%"
  },
  ".cm-completionInfo.cm-completionInfo-right": {
    left: "100%"
  },
  ".cm-completionInfo.cm-completionInfo-left-narrow": {
    right: "30px"
  },
  ".cm-completionInfo.cm-completionInfo-right-narrow": {
    left: "30px"
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
    display: "inline-block",
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
    opacity: "0.6",
    boxSizing: "content-box"
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
var se11 = class {
  constructor(e4, t5, n22, s99) {
    this.field = e4, this.line = t5, this.from = n22, this.to = s99;
  }
};
var oe10 = class i6 {
  constructor(e4, t5, n22) {
    this.field = e4, this.from = t5, this.to = n22;
  }
  map(e4) {
    let t5 = e4.mapPos(this.from, -1, E6.TrackDel), n22 = e4.mapPos(this.to, 1, E6.TrackDel);
    return t5 == null || n22 == null ? null : new i6(this.field, t5, n22);
  }
};
var le9 = class i7 {
  constructor(e4, t5) {
    this.lines = e4, this.fieldPositions = t5;
  }
  instantiate(e4, t5) {
    let n22 = [], s99 = [
      t5
    ], o4 = e4.doc.lineAt(t5), l11 = /^\s*/.exec(o4.text)[0];
    for (let r2 of this.lines) {
      if (n22.length) {
        let f2 = l11, c4 = /^\t*/.exec(r2)[0].length;
        for (let h3 = 0; h3 < c4; h3++) f2 += e4.facet(Wt5);
        s99.push(t5 + f2.length - c4), r2 = f2 + r2.slice(c4);
      }
      n22.push(r2), t5 += r2.length + 1;
    }
    let a2 = this.fieldPositions.map((r2) => new oe10(r2.field, s99[r2.line] + r2.from, s99[r2.line] + r2.to));
    return {
      text: n22,
      ranges: a2
    };
  }
  static parse(e4) {
    let t5 = [], n22 = [], s99 = [], o4;
    for (let l11 of e4.split(/\r\n?|\n/)) {
      for (; o4 = /[#$]\{(?:(\d+)(?::([^}]*))?|((?:\\[{}]|[^}])*))\}/.exec(l11); ) {
        let a2 = o4[1] ? +o4[1] : null, r2 = o4[2] || o4[3] || "", f2 = -1, c4 = r2.replace(/\\[{}]/g, (h3) => h3[1]);
        for (let h3 = 0; h3 < t5.length; h3++) (a2 != null ? t5[h3].seq == a2 : c4 && t5[h3].name == c4) && (f2 = h3);
        if (f2 < 0) {
          let h3 = 0;
          for (; h3 < t5.length && (a2 == null || t5[h3].seq != null && t5[h3].seq < a2); ) h3++;
          t5.splice(h3, 0, {
            seq: a2,
            name: c4
          }), f2 = h3;
          for (let u5 of s99) u5.field >= f2 && u5.field++;
        }
        s99.push(new se11(f2, n22.length, o4.index, o4.index + c4.length)), l11 = l11.slice(0, o4.index) + r2 + l11.slice(o4.index + o4[0].length);
      }
      l11 = l11.replace(/\\([{}])/g, (a2, r2, f2) => {
        for (let c4 of s99) c4.line == n22.length && c4.from > f2 && (c4.from--, c4.to--);
        return r2;
      }), n22.push(l11);
    }
    return new i7(n22, s99);
  }
};
var xt6 = T8.widget({
  widget: new class extends et4 {
    toDOM() {
      let i9 = document.createElement("span");
      return i9.className = "cm-snippetFieldPosition", i9;
    }
    ignoreEvent() {
      return false;
    }
  }()
});
var wt6 = T8.mark({
  class: "cm-snippetField"
});
var P11 = class i8 {
  constructor(e4, t5) {
    this.ranges = e4, this.active = t5, this.deco = T8.set(e4.map((n22) => (n22.from == n22.to ? xt6 : wt6).range(n22.from, n22.to)));
  }
  map(e4) {
    let t5 = [];
    for (let n22 of this.ranges) {
      let s99 = n22.map(e4);
      if (!s99) return null;
      t5.push(s99);
    }
    return new i8(t5, this.active);
  }
  selectionInsideField(e4) {
    return e4.ranges.every((t5) => this.ranges.some((n22) => n22.field == this.active && n22.from <= t5.from && n22.to >= t5.to));
  }
};
var j11 = v5.define({
  map(i9, e4) {
    return i9 && i9.map(e4);
  }
});
var Ct7 = v5.define();
var E11 = z8.define({
  create() {
    return null;
  },
  update(i9, e4) {
    for (let t5 of e4.effects) {
      if (t5.is(j11)) return t5.value;
      if (t5.is(Ct7) && i9) return new P11(i9.ranges, t5.value);
    }
    return i9 && e4.docChanged && (i9 = i9.map(e4.changes)), i9 && e4.selection && !i9.selectionInsideField(e4.selection) && (i9 = null), i9;
  },
  provide: (i9) => k8.decorations.from(i9, (e4) => e4 ? e4.deco : T8.none)
});
function pe9(i9, e4) {
  return x8.create(i9.filter((t5) => t5.field == e4).map((t5) => x8.range(t5.from, t5.to)));
}
function St7(i9) {
  let e4 = le9.parse(i9);
  return (t5, n22, s99, o4) => {
    let { text: l11, ranges: a2 } = e4.instantiate(t5.state, s99), { main: r2 } = t5.state.selection, f2 = {
      changes: {
        from: s99,
        to: o4 == r2.from ? r2.to : o4,
        insert: m7.of(l11)
      },
      scrollIntoView: true,
      annotations: n22 ? [
        ce12.of(n22),
        S7.userEvent.of("input.complete")
      ] : void 0
    };
    if (a2.length && (f2.selection = pe9(a2, 0)), a2.some((c4) => c4.field > 0)) {
      let c4 = new P11(a2, 0), h3 = f2.effects = [
        j11.of(c4)
      ];
      t5.state.field(E11, false) === void 0 && h3.push(v5.appendConfig.of([
        E11,
        Et6,
        Dt7,
        ke10
      ]));
    }
    t5.dispatch(t5.state.update(f2));
  };
}
function Be9(i9) {
  return ({ state: e4, dispatch: t5 }) => {
    let n22 = e4.field(E11, false);
    if (!n22 || i9 < 0 && n22.active == 0) return false;
    let s99 = n22.active + i9, o4 = i9 > 0 && !n22.ranges.some((l11) => l11.field == s99 + i9);
    return t5(e4.update({
      selection: pe9(n22.ranges, s99),
      effects: j11.of(o4 ? null : new P11(n22.ranges, s99)),
      scrollIntoView: true
    })), true;
  };
}
var It7 = ({ state: i9, dispatch: e4 }) => i9.field(E11, false) ? (e4(i9.update({
  effects: j11.of(null)
})), true) : false;
var Ot6 = Be9(1);
var Tt8 = Be9(-1);
function Xt7(i9) {
  let e4 = i9.field(E11, false);
  return !!(e4 && e4.ranges.some((t5) => t5.field == e4.active + 1));
}
function Yt5(i9) {
  let e4 = i9.field(E11, false);
  return !!(e4 && e4.active > 0);
}
var At5 = [
  {
    key: "Tab",
    run: Ot6,
    shift: Tt8
  },
  {
    key: "Escape",
    run: It7
  }
];
var we9 = k7.define({
  combine(i9) {
    return i9.length ? i9[0] : At5;
  }
});
var Et6 = st4.highest(kr2.compute([
  we9
], (i9) => i9.facet(we9)));
function Gt5(i9, e4) {
  return Object.assign(Object.assign({}, e4), {
    apply: St7(i9)
  });
}
var Dt7 = k8.domEventHandlers({
  mousedown(i9, e4) {
    let t5 = e4.state.field(E11, false), n22;
    if (!t5 || (n22 = e4.posAtCoords({
      x: i9.clientX,
      y: i9.clientY
    })) == null) return false;
    let s99 = t5.ranges.find((o4) => o4.from <= n22 && o4.to >= n22);
    return !s99 || s99.field == t5.active ? false : (e4.dispatch({
      selection: pe9(t5.ranges, s99.field),
      effects: j11.of(t5.ranges.some((o4) => o4.field > s99.field) ? new P11(t5.ranges, s99.field) : null),
      scrollIntoView: true
    }), true);
  }
});
function Pt6(i9) {
  let e4 = i9.replace(/[\]\-\\]/g, "\\$&");
  try {
    return new RegExp(`[\\p{Alphabetic}\\p{Number}_${e4}]+`, "ug");
  } catch {
    return new RegExp(`[w${e4}]`, "g");
  }
}
function Ce11(i9, e4) {
  return new RegExp(e4(i9.source), i9.unicode ? "u" : "");
}
var Se11 = /* @__PURE__ */ Object.create(null);
function Rt6(i9) {
  return Se11[i9] || (Se11[i9] = /* @__PURE__ */ new WeakMap());
}
function Ie10(i9, e4, t5, n22, s99) {
  for (let o4 = i9.iterLines(), l11 = 0; !o4.next().done; ) {
    let { value: a2 } = o4, r2;
    for (e4.lastIndex = 0; r2 = e4.exec(a2); ) if (!n22[r2[0]] && l11 + r2.index != s99 && (t5.push({
      type: "text",
      label: r2[0]
    }), n22[r2[0]] = true, t5.length >= 2e3)) return;
    l11 += a2.length + 1;
  }
}
function je8(i9, e4, t5, n22, s99) {
  let o4 = i9.length >= 1e3, l11 = o4 && e4.get(i9);
  if (l11) return l11;
  let a2 = [], r2 = /* @__PURE__ */ Object.create(null);
  if (i9.children) {
    let f2 = 0;
    for (let c4 of i9.children) {
      if (c4.length >= 1e3) for (let h3 of je8(c4, e4, t5, n22 - f2, s99 - f2)) r2[h3.label] || (r2[h3.label] = true, a2.push(h3));
      else Ie10(c4, t5, a2, r2, s99 - f2);
      f2 += c4.length + 1;
    }
  } else Ie10(i9, t5, a2, r2, s99);
  return o4 && a2.length < 2e3 && e4.set(i9, a2), a2;
}
var Jt6 = (i9) => {
  let e4 = i9.state.languageDataAt("wordChars", i9.pos).join(""), t5 = Pt6(e4), n22 = i9.matchBefore(Ce11(t5, (l11) => l11 + "$"));
  if (!n22 && !i9.explicit) return null;
  let s99 = n22 ? n22.from : i9.pos, o4 = je8(i9.state.doc, Rt6(e4), t5, 5e4, s99);
  return {
    from: s99,
    options: o4,
    validFor: Ce11(t5, (l11) => "^" + l11)
  };
};
var k12 = {
  brackets: [
    "(",
    "[",
    "{",
    "'",
    '"'
  ],
  before: ")]}:;>",
  stringPrefixes: []
};
var T11 = v5.define({
  map(i9, e4) {
    let t5 = e4.mapPos(i9, -1, E6.TrackAfter);
    return t5 ?? void 0;
  }
});
var de12 = new class extends q7 {
}();
de12.startSide = 1;
de12.endSide = -1;
var $e6 = z8.define({
  create() {
    return T7.empty;
  },
  update(i9, e4) {
    if (i9 = i9.map(e4.changes), e4.selection) {
      let t5 = e4.state.doc.lineAt(e4.selection.main.head);
      i9 = i9.update({
        filter: (n22) => n22 >= t5.from && n22 <= t5.to
      });
    }
    for (let t5 of e4.effects) t5.is(T11) && (i9 = i9.update({
      add: [
        de12.range(t5.value, t5.value + 1)
      ]
    }));
    return i9;
  }
});
function Zt5() {
  return [
    Mt6,
    $e6
  ];
}
var X13 = "()[]{}<>";
function Fe10(i9) {
  for (let e4 = 0; e4 < X13.length; e4 += 2) if (X13.charCodeAt(e4) == i9) return X13.charAt(e4 + 1);
  return nt3(i9 < 128 ? i9 : i9 + 1);
}
function We9(i9, e4) {
  return i9.languageDataAt("closeBrackets", e4)[0] || k12;
}
var Lt7 = typeof navigator == "object" && /Android\b/.test(navigator.userAgent);
var Mt6 = k8.inputHandler.of((i9, e4, t5, n22) => {
  if ((Lt7 ? i9.composing : i9.compositionStarted) || i9.state.readOnly) return false;
  let s99 = i9.state.selection.main;
  if (n22.length > 2 || n22.length == 2 && it5(tt5(n22, 0)) == 1 || e4 != s99.from || t5 != s99.to) return false;
  let o4 = Bt6(i9.state, n22);
  return o4 ? (i9.dispatch(o4), true) : false;
});
var kt6 = ({ state: i9, dispatch: e4 }) => {
  if (i9.readOnly) return false;
  let n22 = We9(i9, i9.selection.main.head).brackets || k12.brackets, s99 = null, o4 = i9.changeByRange((l11) => {
    if (l11.empty) {
      let a2 = jt7(i9.doc, l11.head);
      for (let r2 of n22) if (r2 == a2 && q12(i9.doc, l11.head) == Fe10(tt5(r2, 0))) return {
        changes: {
          from: l11.head - r2.length,
          to: l11.head + r2.length
        },
        range: x8.cursor(l11.head - r2.length)
      };
    }
    return {
      range: s99 = l11
    };
  });
  return s99 || e4(i9.update(o4, {
    scrollIntoView: true,
    userEvent: "delete.backward"
  })), !s99;
};
var _t6 = [
  {
    key: "Backspace",
    run: kt6
  }
];
function Bt6(i9, e4) {
  let t5 = We9(i9, i9.selection.main.head), n22 = t5.brackets || k12.brackets;
  for (let s99 of n22) {
    let o4 = Fe10(tt5(s99, 0));
    if (e4 == s99) return o4 == s99 ? Wt6(i9, s99, n22.indexOf(s99 + s99 + s99) > -1, t5) : $t6(i9, s99, o4, t5.before || k12.before);
    if (e4 == o4 && Ne9(i9, i9.selection.main.from)) return Ft6(i9, s99, o4);
  }
  return null;
}
function Ne9(i9, e4) {
  let t5 = false;
  return i9.field($e6).between(0, i9.doc.length, (n22) => {
    n22 == e4 && (t5 = true);
  }), t5;
}
function q12(i9, e4) {
  let t5 = i9.sliceString(e4, e4 + 2);
  return t5.slice(0, it5(tt5(t5, 0)));
}
function jt7(i9, e4) {
  let t5 = i9.sliceString(e4 - 2, e4);
  return it5(tt5(t5, 0)) == t5.length ? t5 : t5.slice(1);
}
function $t6(i9, e4, t5, n22) {
  let s99 = null, o4 = i9.changeByRange((l11) => {
    if (!l11.empty) return {
      changes: [
        {
          insert: e4,
          from: l11.from
        },
        {
          insert: t5,
          from: l11.to
        }
      ],
      effects: T11.of(l11.to + e4.length),
      range: x8.range(l11.anchor + e4.length, l11.head + e4.length)
    };
    let a2 = q12(i9.doc, l11.head);
    return !a2 || /\s/.test(a2) || n22.indexOf(a2) > -1 ? {
      changes: {
        insert: e4 + t5,
        from: l11.head
      },
      effects: T11.of(l11.head + e4.length),
      range: x8.cursor(l11.head + e4.length)
    } : {
      range: s99 = l11
    };
  });
  return s99 ? null : i9.update(o4, {
    scrollIntoView: true,
    userEvent: "input.type"
  });
}
function Ft6(i9, e4, t5) {
  let n22 = null, s99 = i9.changeByRange((o4) => o4.empty && q12(i9.doc, o4.head) == t5 ? {
    changes: {
      from: o4.head,
      to: o4.head + t5.length,
      insert: t5
    },
    range: x8.cursor(o4.head + t5.length)
  } : n22 = {
    range: o4
  });
  return n22 ? null : i9.update(s99, {
    scrollIntoView: true,
    userEvent: "input.type"
  });
}
function Wt6(i9, e4, t5, n22) {
  let s99 = n22.stringPrefixes || k12.stringPrefixes, o4 = null, l11 = i9.changeByRange((a2) => {
    if (!a2.empty) return {
      changes: [
        {
          insert: e4,
          from: a2.from
        },
        {
          insert: e4,
          from: a2.to
        }
      ],
      effects: T11.of(a2.to + e4.length),
      range: x8.range(a2.anchor + e4.length, a2.head + e4.length)
    };
    let r2 = a2.head, f2 = q12(i9.doc, r2), c4;
    if (f2 == e4) {
      if (Oe9(i9, r2)) return {
        changes: {
          insert: e4 + e4,
          from: r2
        },
        effects: T11.of(r2 + e4.length),
        range: x8.cursor(r2 + e4.length)
      };
      if (Ne9(i9, r2)) {
        let u5 = t5 && i9.sliceDoc(r2, r2 + e4.length * 3) == e4 + e4 + e4 ? e4 + e4 + e4 : e4;
        return {
          changes: {
            from: r2,
            to: r2 + u5.length,
            insert: u5
          },
          range: x8.cursor(r2 + u5.length)
        };
      }
    } else {
      if (t5 && i9.sliceDoc(r2 - 2 * e4.length, r2) == e4 + e4 && (c4 = Te11(i9, r2 - 2 * e4.length, s99)) > -1 && Oe9(i9, c4)) return {
        changes: {
          insert: e4 + e4 + e4 + e4,
          from: r2
        },
        effects: T11.of(r2 + e4.length),
        range: x8.cursor(r2 + e4.length)
      };
      if (i9.charCategorizer(r2)(f2) != M9.Word && Te11(i9, r2, s99) > -1 && !Nt5(i9, r2, e4, s99)) return {
        changes: {
          insert: e4 + e4,
          from: r2
        },
        effects: T11.of(r2 + e4.length),
        range: x8.cursor(r2 + e4.length)
      };
    }
    return {
      range: o4 = a2
    };
  });
  return o4 ? null : i9.update(l11, {
    scrollIntoView: true,
    userEvent: "input.type"
  });
}
function Oe9(i9, e4) {
  let t5 = k11(i9).resolveInner(e4 + 1);
  return t5.parent && t5.from == e4;
}
function Nt5(i9, e4, t5, n22) {
  let s99 = k11(i9).resolveInner(e4, -1), o4 = n22.reduce((l11, a2) => Math.max(l11, a2.length), 0);
  for (let l11 = 0; l11 < 5; l11++) {
    let a2 = i9.sliceDoc(s99.from, Math.min(s99.to, s99.from + t5.length + o4)), r2 = a2.indexOf(t5);
    if (!r2 || r2 > -1 && n22.indexOf(a2.slice(0, r2)) > -1) {
      let c4 = s99.firstChild;
      for (; c4 && c4.from == s99.from && c4.to - c4.from > t5.length + r2; ) {
        if (i9.sliceDoc(c4.to - t5.length, c4.to) == t5) return false;
        c4 = c4.firstChild;
      }
      return true;
    }
    let f2 = s99.to == e4 && s99.parent;
    if (!f2) break;
    s99 = f2;
  }
  return false;
}
function Te11(i9, e4, t5) {
  let n22 = i9.charCategorizer(e4);
  if (n22(i9.sliceDoc(e4 - 1, e4)) != M9.Word) return e4;
  for (let s99 of t5) {
    let o4 = e4 - s99.length;
    if (i9.sliceDoc(o4, e4) == s99 && n22(i9.sliceDoc(o4 - 1, o4)) != M9.Word) return o4;
  }
  return -1;
}
function ei3(i9 = {}) {
  return [
    vt5,
    m8,
    g5.of(i9),
    bt7,
    Vt4,
    ke10
  ];
}
var Ut7 = [
  {
    key: "Ctrl-Space",
    run: xe11
  },
  {
    mac: "Alt-`",
    run: xe11
  },
  {
    key: "Escape",
    run: dt5
  },
  {
    key: "ArrowDown",
    run: F12(true)
  },
  {
    key: "ArrowUp",
    run: F12(false)
  },
  {
    key: "PageDown",
    run: F12(true, "page")
  },
  {
    key: "PageUp",
    run: F12(false, "page")
  },
  {
    key: "Enter",
    run: pt6
  }
];
var Vt4 = st4.highest(kr2.computeN([
  g5
], (i9) => i9.facet(g5).defaultKeymap ? [
  Ut7
] : []));
function ti3(i9) {
  let e4 = i9.field(m8, false);
  return e4 && e4.active.some((t5) => t5.isPending) ? "pending" : e4 && e4.active.some((t5) => t5.state != 0) ? "active" : null;
}
var Ae9 = /* @__PURE__ */ new WeakMap();
function ii3(i9) {
  var e4;
  let t5 = (e4 = i9.field(m8, false)) === null || e4 === void 0 ? void 0 : e4.open;
  if (!t5 || t5.disabled) return [];
  let n22 = Ae9.get(t5.options);
  return n22 || Ae9.set(t5.options, n22 = t5.options.map((s99) => s99.completion)), n22;
}
function ni3(i9) {
  var e4;
  let t5 = (e4 = i9.field(m8, false)) === null || e4 === void 0 ? void 0 : e4.open;
  return t5 && !t5.disabled && t5.selected >= 0 ? t5.options[t5.selected].completion : null;
}
function si3(i9) {
  var e4;
  let t5 = (e4 = i9.field(m8, false)) === null || e4 === void 0 ? void 0 : e4.open;
  return t5 && !t5.disabled && t5.selected >= 0 ? t5.selected : null;
}
function oi3(i9) {
  return he9.of(i9);
}
export {
  W11 as CompletionContext,
  tt7 as DocInput,
  I as EditorState,
  M2 as EditorView,
  z11 as HighlightStyle,
  N12 as IndentContext,
  bt5 as LRLanguage,
  d3 as Language,
  vt4 as LanguageDescription,
  yt5 as LanguageSupport,
  M11 as ParseContext,
  Pt5 as StreamLanguage,
  q11 as StringStream,
  et6 as TreeIndentContext,
  pt6 as acceptCompletion,
  ei3 as autocompletion,
  I7 as basicSetup,
  Pn3 as bidiIsolates,
  Sn3 as bracketMatching,
  Ve6 as bracketMatchingHandle,
  It7 as clearSnippet,
  Zt5 as closeBrackets,
  _t6 as closeBracketsKeymap,
  dt5 as closeCompletion,
  zt4 as codeFolding,
  Jt6 as completeAnyWord,
  _e9 as completeFromList,
  Ut7 as completionKeymap,
  ti3 as completionStatus,
  pn2 as continuedIndent,
  ii3 as currentCompletions,
  Tn4 as defaultHighlightStyle,
  Lt6 as defineLanguageFacet,
  kt6 as deleteBracketPair,
  cn3 as delimitedIndent,
  de10 as ensureSyntaxTree,
  dn3 as flatIndent,
  De9 as foldAll,
  Ce9 as foldCode,
  F10 as foldEffect,
  yn3 as foldGutter,
  gn3 as foldInside,
  wn3 as foldKeymap,
  Te9 as foldNodeProp,
  xe10 as foldService,
  T9 as foldState,
  L9 as foldable,
  kn3 as foldedRanges,
  an4 as forceParsing,
  V11 as getIndentUnit,
  Wt4 as getIndentation,
  Xt7 as hasNextSnippetField,
  Yt5 as hasPrevSnippetField,
  xn3 as highlightingFor,
  zt5 as ifIn,
  Qt7 as ifNotIn,
  jt6 as indentNodeProp,
  mn2 as indentOnInput,
  un3 as indentRange,
  pe8 as indentService,
  Ut5 as indentString,
  Ft4 as indentUnit,
  Bt6 as insertBracket,
  et7 as insertCompletionText,
  x9 as language,
  S8 as languageDataProp,
  U11 as matchBrackets,
  F12 as moveCompletionSelection,
  Ot6 as nextSnippetField,
  ce12 as pickedCompletion,
  Tt8 as prevSnippetField,
  ni3 as selectedCompletion,
  si3 as selectedCompletionIndex,
  oi3 as setSelectedCompletion,
  St7 as snippet,
  Gt5 as snippetCompletion,
  we9 as snippetKeymap,
  xe11 as startCompletion,
  ce11 as sublanguageProp,
  vn3 as syntaxHighlighting,
  fn2 as syntaxParserRunning,
  k10 as syntaxTree,
  ln4 as syntaxTreeAvailable,
  bn3 as toggleFold,
  Oe8 as unfoldAll,
  Ie9 as unfoldCode,
  C10 as unfoldEffect
};
