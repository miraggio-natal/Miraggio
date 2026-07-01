const test = require('node:test');
const assert = require('node:assert/strict');
const { createApp } = require('../server');

function buildRequest(app) {
  return async (method, path, body) => {
    const res = await new Promise((resolve) => {
      const req = require('http').request(
        {
          hostname: '127.0.0.1',
          port: 0,
          path,
          method,
          headers: { 'content-type': 'application/json' }
        },
        (response) => {
          let data = '';
          response.on('data', (chunk) => { data += chunk; });
          response.on('end', () => resolve({ statusCode: response.statusCode, body: data }));
        }
      );

      req.on('error', () => resolve({ statusCode: 500, body: '{}' }));
      req.write(JSON.stringify(body || {}));
      req.end();
    });

    return res;
  };
}

test('GET /health returns ok', async () => {
  const app = createApp();
  const server = app.listen(0);
  const { port } = server.address();

  const response = await new Promise((resolve, reject) => {
    const req = require('http').get({ hostname: '127.0.0.1', port, path: '/health' }, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => resolve({ statusCode: res.statusCode, body: data }));
    });
    req.on('error', reject);
  });

  server.close();
  assert.equal(response.statusCode, 200);
  assert.match(response.body, /"status":"ok"/);
});

test('POST /api/auth/login authenticates admin user', async () => {
  const app = createApp();
  const server = app.listen(0);
  const { port } = server.address();

  const response = await new Promise((resolve, reject) => {
    const req = require('http').request({
      hostname: '127.0.0.1',
      port,
      path: '/api/auth/login',
      method: 'POST',
      headers: { 'content-type': 'application/json' }
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => resolve({ statusCode: res.statusCode, body: data }));
    });

    req.write(JSON.stringify({ email: 'admin@empresa.local', password: 'Trocar@123' }));
    req.end();
  });

  server.close();
  assert.equal(response.statusCode, 200);
  assert.match(response.body, /"token"/);
});
