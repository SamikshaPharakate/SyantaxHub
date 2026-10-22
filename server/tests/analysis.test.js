const assert = require('assert');
const aiMicroservice = require('../src/services/aiMicroservice');

async function runTests() {
  console.log('--- Running SyntaxHub Analysis Accuracy Tests (Node.js Engine) ---');
  let passed = 0;
  let failed = 0;

  // Test 1: Valid React 19 code -> status == 'current'
  try {
    const validReact19 = `
import { useState } from 'react';

export function ModernProfile({ name, ref }) {
  const [likes, setLikes] = useState(0);
  return (
    <div ref={ref}>
      <h2>{name}</h2>
      <button onClick={() => setLikes(likes + 1)}>Likes: {likes}</button>
    </div>
  );
}
`;
    // We test the static analysis engine directly (fallback) by ensuring aiMicroservice evaluates code
    const res = await aiMicroservice.analyzeCode({
      code: validReact19,
      language: 'javascript',
      technology: 'React',
      version: '19'
    });

    const status = res.data ? res.data.status : res.status;
    assert.strictEqual(status, 'current', `Expected 'current' for valid React 19, got '${status}'`);
    console.log('✅ Test 1 Passed: Valid React 19 code classified as CURRENT');
    passed++;
  } catch (err) {
    console.error('❌ Test 1 Failed:', err.message);
    failed++;
  }

  // Test 2: Deprecated JavaScript substr() -> status == 'outdated'
  try {
    const deprecatedJs = `
const extractDomain = (email) => {
  const at = email.indexOf('@');
  return email.substr(at + 1);
};
`;
    const res = await aiMicroservice.analyzeCode({
      code: deprecatedJs,
      language: 'javascript',
      technology: 'JavaScript',
      version: 'ES2024'
    });

    const status = res.data ? res.data.status : res.status;
    assert.strictEqual(status, 'outdated', `Expected 'outdated' for substr(), got '${status}'`);
    console.log('✅ Test 2 Passed: Deprecated JavaScript substr() classified as OUTDATED');
    passed++;
  } catch (err) {
    console.error('❌ Test 2 Failed:', err.message);
    failed++;
  }

  // Test 3: Valid JavaScript slice() -> status == 'current'
  try {
    const validJs = `
const extractDomain = (email) => {
  const at = email.indexOf('@');
  return email.slice(at + 1);
};
`;
    const res = await aiMicroservice.analyzeCode({
      code: validJs,
      language: 'javascript',
      technology: 'JavaScript',
      version: 'ES2024'
    });

    const status = res.data ? res.data.status : res.status;
    assert.strictEqual(status, 'current', `Expected 'current' for slice(), got '${status}'`);
    console.log('✅ Test 3 Passed: Valid JavaScript slice() classified as CURRENT');
    passed++;
  } catch (err) {
    console.error('❌ Test 3 Failed:', err.message);
    failed++;
  }

  // Test 4: Insufficient evidence -> status == 'uncertain'
  try {
    const emptyCode = `   `;
    const res = await aiMicroservice.analyzeCode({
      code: emptyCode,
      language: 'javascript',
      technology: 'JavaScript',
      version: 'ES2024'
    });

    const status = res.data ? res.data.status : res.status;
    assert.strictEqual(status, 'uncertain', `Expected 'uncertain' for empty code, got '${status}'`);
    console.log('✅ Test 4 Passed: Insufficient code returns UNCERTAIN');
    passed++;
  } catch (err) {
    console.error('❌ Test 4 Failed:', err.message);
    failed++;
  }

  console.log(`\nResults: ${passed} passed, ${failed} failed`);
  if (failed > 0) {
    process.exit(1);
  }
}

runTests();
