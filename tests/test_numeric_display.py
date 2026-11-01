"""Regression for the observed decimal tie display bug. Needs an existing Node; no install."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json,re,subprocess,shutil,unittest
ROOT=Path(__file__).resolve().parents[1]
NODE=shutil.which('node')
class NumericDisplay(unittest.TestCase):
    @unittest.skipUnless(NODE,'Existing Node unavailable; numeric JS tests not executed')
    def test_exact_ratios_and_boundaries(self):
        text=(ROOT/'skills/explain-clearly/assets/explainer.html').read_text()
        match=re.search(r'  function formatRatio\(.*?\n  \}',text,re.S)
        self.assertIsNotNone(match,'template formatter must remain available for this regression')
        cases=[
            (975,1000,2,False),(974,1000,2,False),(976,1000,2,False),
            (165,100,1,True),(1649,1000,1,True),(1651,1000,1,True),
            (-165,100,1,True),(8000,100,1,True),(0,10,2,False),
            (5,2,0,False),(1,200,2,False),(39,40,2,False),
        ]
        script=match.group(0)+'\nconsole.log(JSON.stringify('+json.dumps(cases)+'.map(c => formatRatio(...c))));'
        result=subprocess.run([NODE,'-e',script],text=True,capture_output=True,check=True)
        actual=json.loads(result.stdout)
        for case,value in zip(cases,actual):
            n,d,digits,trim=case
            expected=format((Decimal(n)/Decimal(d)).quantize(Decimal(1).scaleb(-digits),rounding=ROUND_HALF_UP),'f')
            if trim and digits:expected=expected.rstrip('0').rstrip('.')
            with self.subTest(case=case):self.assertEqual(value,expected)
    @unittest.skipUnless(NODE,'Existing Node unavailable; rejection checks not executed')
    def test_invalid_denominator_rejected(self):
        text=(ROOT/'skills/explain-clearly/assets/explainer.html').read_text()
        fn=re.search(r'  function formatRatio\(.*?\n  \}',text,re.S).group(0)
        script=fn+"\ntry { formatRatio(1,0,2); process.exit(1); } catch(e) { if (!(e instanceof RangeError)) process.exit(2); }"
        subprocess.run([NODE,'-e',script],check=True)

    @unittest.skipUnless(NODE, 'Existing Node unavailable; rendered comparisons not executed')
    def test_slider_comparisons(self):
        page = (ROOT / 'examples/interactive.html').read_text()
        script = re.search(r'<script>(.*?)</script>', page, re.S).group(1)
        dom = """
const elements = new Map();
const document = {
  getElementById(id) {
    if (!elements.has(id)) elements.set(id, {
      id, style: {}, setAttribute() {},
      addEventListener(event, handler) { this[event] = handler; }
    });
    return elements.get(id);
  }
};
const get = id => document.getElementById(id);
function sliders(hit, fast, slow) {
  get('hit').value = hit; get('fast').value = fast; get('slow').value = slow;
}
sliders(40, 20, 120);
"""
        read_results = """
for (const values of [[41, 120, 121], [39, 120, 121], [41, 200, 201], [65, 20, 120], [40, 20, 120]]) {
  sliders(...values);
  get('hit').input();
  console.log(JSON.stringify(['mean', 'base-number', 'current-number', 'comparison']
    .map(id => get(id).textContent)));
}
"""
        run = subprocess.run([NODE, '-e', dom + script + read_results],
                             check=True, text=True, capture_output=True)
        actual = [json.loads(line) for line in run.stdout.splitlines()]
        expected = [
            ('120.59', '120.6', '减少 0.01 毫秒（下降 0.008%）。'),
            ('120.61', '120.6', '增加 0.01 毫秒（上升 0.008%）。'),
            ('200.59', '200.6', '减少 0.01 毫秒（下降 0.005%）。'),
            ('55', '80', '减少 25 毫秒（下降 31.3%）。'),
            ('80', '80', '基准相同。'),
        ]
        self.assertEqual(len(actual), len(expected))
        for displayed, (mean, baseline, comparison) in zip(actual, expected):
            with self.subTest(mean=mean):
                self.assertEqual(displayed[:3], [mean, baseline + ' 毫秒', mean + ' 毫秒'])
                self.assertTrue(displayed[3].endswith(comparison), displayed[3])

if __name__=='__main__':unittest.main(verbosity=2)
