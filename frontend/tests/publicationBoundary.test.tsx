import test from 'node:test';
import assert from 'node:assert/strict';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { MonoResultView, monthLabel } from '../src/components/mono/MonoResults';
import { historicalDownloadName } from '../src/lib/monoPublicationLabels';
import type { MonoResult } from '../src/lib/monoApi';

const result = (value: unknown) => ({ result_id: 'invented', checks: {release_passed:true},
  outputs:{out_irr_gross:null}, output_metadata:{out_irr_gross:{unit:'%',applicability:{status:'applies'},
    availability:{status:'total_loss',reason:'loss',display_text:value}}}, identity:{}, artifact_sha256:'invented' }) as unknown as MonoResult;

test('missing total-loss labels are unavailable rather than fake values',()=>{
  for(const value of [undefined,null,'','   ']) {
    const html=renderToStaticMarkup(<MonoResultView result={result(value)}/>);
    assert.ok(html.includes('Unavailable'));
    assert.ok(!html.includes('>Empty text<'));
  }
});

test('historical available flags cannot release nonnumeric financial values',()=>{
  for(const value of [undefined,null,NaN,Infinity,'123']) {
    const sample=result('Total loss');
    sample.selected_financial_projection={provider_id:'esplanade_historical_annual_v1',
      historical_profile:{comparison_month:'2026-09'},metrics:{historical_net_operating_income_y1:{availability:'available',value,unit:'USD/year'}}} as any;
    const html=renderToStaticMarkup(<MonoResultView result={sample}/>);
    const card=html.split('data-output-id="historical_net_operating_income_y1"')[1].split('</div>')[0];
    assert.ok(card.includes('Unavailable'));
  }
});

test('release failure withholds historical figures too',()=>{
  const sample=result('Total loss'); sample.checks={release_passed:false};
  sample.selected_financial_projection={provider_id:'esplanade_historical_annual_v1',historical_profile:{comparison_month:'2026-09'},
    metrics:{historical_net_operating_income_y1:{availability:'available',value:123,unit:'USD/year'}}} as any;
  assert.ok(!renderToStaticMarkup(<MonoResultView result={sample}/>).includes('$123.00'));
});

test('historical downloads require a valid comparison month',()=>{
  for(const month of [undefined,null,'','2026-00','2026-13','bad','0000-01']) {
    assert.equal(historicalDownloadName('memo.pdf',month),null);
    assert.ok(monthLabel(month).includes('Unavailable'));
  }
  assert.equal(historicalDownloadName('memo.pdf','2026-09'),'historical-source-comparison-2026-09-memo.pdf');
});

test('a genuine available zero remains a numeric result',()=>{
  const sample=result('Total loss');
  sample.selected_financial_projection={provider_id:'esplanade_historical_annual_v1',historical_profile:{comparison_month:'2026-09'},
    metrics:{historical_net_operating_income_y1:{availability:'available',value:0,unit:'USD/year'}}} as any;
  assert.ok(renderToStaticMarkup(<MonoResultView result={sample}/>).includes('$0.00'));
});
