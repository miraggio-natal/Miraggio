const express = require('express');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

const dataFilePath = path.join(__dirname, 'data', 'employees.json');

function loadEmployees() {
  if (!fs.existsSync(dataFilePath)) {
    return [
      {
        id: 1,
        fullName: 'Ana Souza',
        email: 'ana.souza@empresa.local',
        role: 'Analista de RH',
        department: 'Recursos Humanos',
        status: 'Ativo',
        hireDate: '2024-01-15',
        manager: 'Carlos Mendes'
      },
      {
        id: 2,
        fullName: 'Bruno Lima',
        email: 'bruno.lima@empresa.local',
        role: 'Desenvolvedor Full Stack',
        department: 'Tecnologia',
        status: 'Ativo',
        hireDate: '2023-08-03',
        manager: 'Marina Alves'
      },
      {
        id: 3,
        fullName: 'Carla Nogueira',
        email: 'carla.nogueira@empresa.local',
        role: 'Coordenadora de Operações',
        department: 'Operações',
        status: 'Em análise',
        hireDate: '2022-11-19',
        manager: 'Eduardo Costa'
      }
    ];
  }

  try {
    const raw = fs.readFileSync(dataFilePath, 'utf8');
    return JSON.parse(raw);
  } catch (error) {
    return [];
  }
}

function saveEmployees(employees) {
  fs.mkdirSync(path.dirname(dataFilePath), { recursive: true });
  fs.writeFileSync(dataFilePath, JSON.stringify(employees, null, 2));
}

let employees = loadEmployees();

if (!employees.length) {
  employees = [
    {
      id: 1,
      fullName: 'Ana Souza',
      email: 'ana.souza@empresa.local',
      role: 'Analista de RH',
      department: 'Recursos Humanos',
      status: 'Ativo',
      hireDate: '2024-01-15',
      manager: 'Carlos Mendes'
    },
    {
      id: 2,
      fullName: 'Bruno Lima',
      email: 'bruno.lima@empresa.local',
      role: 'Desenvolvedor Full Stack',
      department: 'Tecnologia',
      status: 'Ativo',
      hireDate: '2023-08-03',
      manager: 'Marina Alves'
    },
    {
      id: 3,
      fullName: 'Carla Nogueira',
      email: 'carla.nogueira@empresa.local',
      role: 'Coordenadora de Operações',
      department: 'Operações',
      status: 'Em análise',
      hireDate: '2022-11-19',
      manager: 'Eduardo Costa'
    }
  ];
  saveEmployees(employees);
}

function persistEmployees(nextEmployees) {
  employees = nextEmployees;
  saveEmployees(employees);
}

function createToken(payload) {
  const header = Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64url');
  const body = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const signature = crypto.createHash('sha256').update(`${header}.${body}`).digest('hex');
  return `${header}.${body}.${signature}`;
}

function verifyToken(token) {
  if (!token) return null;
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  const [header, body, signature] = parts;
  const expected = crypto.createHash('sha256').update(`${header}.${body}`).digest('hex');
  if (signature !== expected) return null;
  try {
    return JSON.parse(Buffer.from(body, 'base64url').toString('utf8'));
  } catch (_) {
    return null;
  }
}


function createApp() {
  const app = express();
  app.use(express.json());

  const authMiddleware = (req, res, next) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    const payload = verifyToken(token);
    if (!payload) {
      res.status(401).json({ error: 'Token inválido' });
      return;
    }
    req.user = payload;
    next();
  };

  app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  app.post('/api/auth/login', (req, res) => {
    const { email, password } = req.body;
    if (email === 'admin@empresa.local' && password === 'Trocar@123') {
      res.json({
        token: createToken({ sub: email, role: 'admin' }),
        user: { email, role: 'admin', twoFactorRequired: true }
      });
      return;
    }

    res.status(401).json({ error: 'Credenciais inválidas' });
  });

  app.post('/api/auth/verify-2fa', (req, res) => {
    const { code } = req.body;
    if (code === '123456') {
      res.json({ success: true, message: '2FA verificado' });
      return;
    }
    res.status(401).json({ error: 'Código inválido' });
  });

  app.get('/api/me', authMiddleware, (req, res) => {
    res.json({ email: req.user.sub, role: req.user.role, name: 'Administrador' });
  });

  app.get('/api/dashboard', authMiddleware, (req, res) => {
    res.json({
      totalEmployees: employees.length,
      activeEmployees: employees.filter((item) => item.status === 'Ativo').length,
      pendingReview: employees.filter((item) => item.status === 'Em análise').length,
      departments: ['Tecnologia', 'Recursos Humanos', 'Operações']
    });
  });

  app.get('/api/employees', authMiddleware, (req, res) => {
    const query = (req.query.q || '').toLowerCase();
    const filtered = employees.filter((item) => {
      const haystack = `${item.fullName} ${item.department} ${item.role}`.toLowerCase();
      return haystack.includes(query);
    });
    res.json(filtered);
  });

  app.get('/api/employees/:id', authMiddleware, (req, res) => {
    const employee = employees.find((item) => item.id === Number(req.params.id));
    if (!employee) {
      res.status(404).json({ error: 'Colaborador não encontrado' });
      return;
    }
    res.json(employee);
  });

  app.post('/api/employees', authMiddleware, (req, res) => {
    const employee = { id: employees.length + 1, ...req.body };
    const nextEmployees = [...employees, employee];
    persistEmployees(nextEmployees);
    res.status(201).json(employee);
  });

  app.post('/api/public/register', (req, res) => {
    const { fullName, email, role, department } = req.body;
    if (!fullName || !email) {
      res.status(400).json({ error: 'Nome e e-mail são obrigatórios' });
      return;
    }

    const employee = {
      id: employees.length + 1,
      fullName,
      email,
      role: role || 'Novo cadastro',
      department: department || 'Não informado',
      status: 'Em análise',
      hireDate: new Date().toISOString().slice(0, 10),
      manager: 'Em definição'
    };

    const nextEmployees = [...employees, employee];
    persistEmployees(nextEmployees);
    res.status(201).json({ success: true, employee });
  });

  app.put('/api/employees/:id', authMiddleware, (req, res) => {
    const index = employees.findIndex((item) => item.id === Number(req.params.id));
    if (index < 0) {
      res.status(404).json({ error: 'Colaborador não encontrado' });
      return;
    }
    const updatedEmployee = { ...employees[index], ...req.body };
    const nextEmployees = [...employees];
    nextEmployees[index] = updatedEmployee;
    persistEmployees(nextEmployees);
    res.json(updatedEmployee);
  });

  app.delete('/api/employees/:id', authMiddleware, (req, res) => {
    const index = employees.findIndex((item) => item.id === Number(req.params.id));
    if (index < 0) {
      res.status(404).json({ error: 'Colaborador não encontrado' });
      return;
    }
    const nextEmployees = employees.filter((_, itemIndex) => itemIndex !== index);
    persistEmployees(nextEmployees);
    res.status(204).end();
  });

  app.get('/api/audit', authMiddleware, (req, res) => {
    res.json([
      { id: 1, action: 'Login', user: 'admin@empresa.local', at: '2026-07-01T08:30:00Z' },
      { id: 2, action: 'Cadastro de funcionário', user: 'admin@empresa.local', at: '2026-07-01T09:15:00Z' }
    ]);
  });

  const frontendPublic = path.join(__dirname, '..', 'frontend-publico');
  const frontendAdmin = path.join(__dirname, '..', 'frontend-admin');
  app.use('/publico', express.static(frontendPublic));
  app.use('/admin', express.static(frontendAdmin));

  app.get('/', (req, res) => {
    res.sendFile(path.join(frontendAdmin, 'index.html'));
  });

  return app;
}

function startServer(port = 3000) {
  const app = createApp();
  return app.listen(port, () => {
    console.log(`Servidor ativo em http://localhost:${port}`);
  });
}

module.exports = { createApp, startServer, employees };

if (require.main === module) {
  startServer();
}
