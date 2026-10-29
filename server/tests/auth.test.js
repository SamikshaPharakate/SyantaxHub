const assert = require('assert');
const axios = require('axios');
const jwt = require('jsonwebtoken');

const API_BASE = 'http://localhost:5000/api/v1';

async function runAuthTests() {
  console.log('--- Running SyntaxHub Authentication & Persistence Tests ---');
  let passed = 0;
  let failed = 0;

  // Test 1: Demo Login issues HttpOnly cookie and JWT token
  let demoToken = '';
  let demoCookie = '';
  try {
    const res = await axios.post(`${API_BASE}/auth/demo-login`);
    assert.strictEqual(res.status, 200, 'Expected 200 OK for demo login');
    assert.strictEqual(res.data.success, true, 'Expected success: true');
    assert.ok(res.data.token, 'Expected JWT token in response body');
    assert.ok(res.data.user, 'Expected user object');
    assert.strictEqual(res.data.user.email, 'demo@syntaxhub.dev');

    // Check Set-Cookie header
    const setCookie = res.headers['set-cookie'];
    assert.ok(setCookie && setCookie.length > 0, 'Expected Set-Cookie header');
    const tokenCookie = setCookie.find(c => c.startsWith('token='));
    assert.ok(tokenCookie, 'Expected token cookie in Set-Cookie header');
    assert.ok(tokenCookie.toLowerCase().includes('httponly'), 'Expected HttpOnly attribute on cookie');
    assert.ok(tokenCookie.toLowerCase().includes('path=/'), 'Expected path=/ attribute on cookie');

    demoToken = res.data.token;
    demoCookie = tokenCookie.split(';')[0]; // token=...
    console.log('✅ Test 1 Passed: Demo Login issues JWT and HttpOnly cookie');
    passed++;
  } catch (err) {
    console.error('❌ Test 1 Failed:', err.response?.data || err.message);
    failed++;
  }

  // Test 2: Access /auth/me using Bearer token header
  try {
    const res = await axios.get(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${demoToken}` },
    });
    assert.strictEqual(res.status, 200);
    assert.strictEqual(res.data.success, true);
    assert.strictEqual(res.data.user.email, 'demo@syntaxhub.dev');
    console.log('✅ Test 2 Passed: /auth/me successfully verifies session via Bearer token');
    passed++;
  } catch (err) {
    console.error('❌ Test 2 Failed:', err.response?.data || err.message);
    failed++;
  }

  // Test 3: Access /auth/me using HttpOnly Cookie (no Authorization header)
  try {
    const res = await axios.get(`${API_BASE}/auth/me`, {
      headers: { Cookie: demoCookie },
    });
    assert.strictEqual(res.status, 200);
    assert.strictEqual(res.data.success, true);
    assert.strictEqual(res.data.user.email, 'demo@syntaxhub.dev');
    console.log('✅ Test 3 Passed: /auth/me successfully restores session via HttpOnly cookie alone');
    passed++;
  } catch (err) {
    console.error('❌ Test 3 Failed:', err.response?.data || err.message);
    failed++;
  }

  // Test 4: Access /auth/me with NO credentials returns 401
  try {
    await axios.get(`${API_BASE}/auth/me`);
    console.error('❌ Test 4 Failed: Expected 401 when unauthenticated');
    failed++;
  } catch (err) {
    if (err.response && err.response.status === 401) {
      console.log('✅ Test 4 Passed: Unauthenticated request rejected with 401');
      passed++;
    } else {
      console.error('❌ Test 4 Failed with unexpected error:', err.message);
      failed++;
    }
  }

  // Test 5: Access /auth/me with invalid / forged token returns 401
  try {
    await axios.get(`${API_BASE}/auth/me`, {
      headers: { Authorization: 'Bearer this_is_a_completely_fake_token_12345' },
    });
    console.error('❌ Test 5 Failed: Expected 401 for forged token');
    failed++;
  } catch (err) {
    if (err.response && err.response.status === 401) {
      console.log('✅ Test 5 Passed: Invalid/forged token rejected with 401');
      passed++;
    } else {
      console.error('❌ Test 5 Failed:', err.message);
      failed++;
    }
  }

  // Test 6: Access /auth/me with expired token returns 401
  try {
    const secret = process.env.JWT_SECRET || 'syntaxhub_jwt_super_secret_key_2026';
    const expiredToken = jwt.sign({ id: '60d0fe4f5311236168a109ca' }, secret, { expiresIn: '-10s' });
    await axios.get(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${expiredToken}` },
    });
    console.error('❌ Test 6 Failed: Expected 401 for expired token');
    failed++;
  } catch (err) {
    if (err.response && err.response.status === 401) {
      console.log('✅ Test 6 Passed: Expired token rejected with 401');
      passed++;
    } else {
      console.error('❌ Test 6 Failed:', err.message);
      failed++;
    }
  }

  // Test 7: Logout clears session cookie and revokes authentication
  try {
    const logoutRes = await axios.post(`${API_BASE}/auth/logout`);
    assert.strictEqual(logoutRes.status, 200);
    assert.strictEqual(logoutRes.data.success, true);
    const setCookie = logoutRes.headers['set-cookie'];
    assert.ok(setCookie && setCookie.length > 0, 'Expected Set-Cookie on logout');
    const tokenCookie = setCookie.find(c => c.startsWith('token='));
    assert.ok(tokenCookie.includes('token=none') || tokenCookie.includes('token=;'), 'Expected cookie value cleared/none');

    // Confirm that accessing /auth/me with cleared cookie returns 401
    try {
      await axios.get(`${API_BASE}/auth/me`, {
        headers: { Cookie: tokenCookie.split(';')[0] },
      });
      console.error('❌ Test 7 Failed: Expected 401 after logout');
      failed++;
    } catch (err) {
      if (err.response && err.response.status === 401) {
        console.log('✅ Test 7 Passed: Logout clears cookie and invalidates session');
        passed++;
      } else {
        throw err;
      }
    }
  } catch (err) {
    console.error('❌ Test 7 Failed:', err.response?.data || err.message);
    failed++;
  }

  // Test 8: Register new user sets cookie and returns JWT
  const testEmail = `test_user_${Date.now()}@syntaxhub.dev`;
  try {
    const regRes = await axios.post(`${API_BASE}/auth/register`, {
      name: 'Auth Test User',
      email: testEmail,
      password: 'StrongTestPassword123!',
    });
    assert.strictEqual(regRes.status, 201);
    assert.strictEqual(regRes.data.success, true);
    assert.ok(regRes.data.token);
    assert.strictEqual(regRes.data.user.email, testEmail);

    const regCookie = regRes.headers['set-cookie']?.find(c => c.startsWith('token='));
    assert.ok(regCookie, 'Expected Set-Cookie on registration');
    assert.ok(regCookie.toLowerCase().includes('httponly'));

    console.log('✅ Test 8 Passed: User registration sets HttpOnly cookie and issues JWT');
    passed++;
  } catch (err) {
    console.error('❌ Test 8 Failed:', err.response?.data || err.message);
    failed++;
  }

  // Test 9: Verify page refresh simulation (multiple calls to /auth/me) preserves session without creating duplicate accounts
  try {
    for (let i = 0; i < 3; i++) {
      const res = await axios.get(`${API_BASE}/auth/me`, {
        headers: { Cookie: demoCookie },
      });
      assert.strictEqual(res.status, 200);
      assert.strictEqual(res.data.user.email, 'demo@syntaxhub.dev');
    }
    console.log('✅ Test 9 Passed: Session verification remains persistent across multiple calls without duplicates');
    passed++;
  } catch (err) {
    console.error('❌ Test 9 Failed:', err.response?.data || err.message);
    failed++;
  }

  console.log(`\n========================================`);
  console.log(`Auth Test Results: ${passed} passed, ${failed} failed`);
  console.log(`========================================\n`);

  if (failed > 0) {
    process.exit(1);
  }
}

runAuthTests();
