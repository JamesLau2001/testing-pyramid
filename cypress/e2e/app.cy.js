const BASE_URL = 'http://localhost:3000';

function loginAs(username, password) {
  cy.visit(`${BASE_URL}/login`);
  cy.get('input[name="username"]').clear().type(username);
  cy.get('input[name="password"]').clear().type(password);
  cy.get('button[type="submit"]').click();
}

function logout() {
  cy.visit(`${BASE_URL}/logout`);
}

describe('Login page', () => {
  beforeEach(() => {
    cy.visit(`${BASE_URL}/login`);
  });

  it('shows the login form', () => {
    cy.get('h1').contains('Login');
    cy.get('input[name="username"]').should('exist');
    cy.get('input[name="password"]').should('exist');
    cy.get('button[type="submit"]').should('exist');
  });

  it('shows an error for invalid credentials', () => {
    cy.get('input[name="username"]').type('nobody');
    cy.get('input[name="password"]').type('wrongpass');
    cy.get('button[type="submit"]').click();
    cy.contains('Invalid username or password');
  });

  it('redirects to home after successful login', () => {
    loginAs('admin', 'adminpass');
    cy.url().should('eq', `${BASE_URL}/`);
  });
});

describe('Navigation bar', () => {
  it('shows Login link when anonymous', () => {
    cy.visit(`${BASE_URL}/`);
    cy.get('nav').contains('Login');
    cy.get('nav').should('not.contain', 'Logout');
  });

  it('shows username and Logout when logged in', () => {
    loginAs('admin', 'adminpass');
    cy.get('nav').contains('admin');
    cy.get('nav').contains('Logout');
  });

  it('shows admin links only for admin role', () => {
    loginAs('admin', 'adminpass');
    cy.get('nav').contains('Manage Coins');
    cy.get('nav').contains('Manage Duties');
    cy.get('nav').contains('Logs');
  });

  it('does not show admin links for authenticated (non-admin) user', () => {
    loginAs('user', 'userpass');
    cy.get('nav').should('not.contain', 'Manage Coins');
    cy.get('nav').should('not.contain', 'Manage Duties');
    cy.get('nav').should('not.contain', 'Logs');
  });

  it('logs out and returns to anonymous state', () => {
    loginAs('admin', 'adminpass');
    cy.contains('Logout').click();
    cy.get('nav').contains('Login');
    cy.get('nav').should('not.contain', 'Logout');
  });
});

describe('Home page (Coins index)', () => {
  it('shows the Coins heading for anonymous users', () => {
    cy.visit(`${BASE_URL}/`);
    cy.get('h1').contains('Coins');
  });

  it('shows coin list or empty message', () => {
    cy.visit(`${BASE_URL}/`);
    cy.get('body').then(($body) => {
      if ($body.find('ul li').length > 0) {
        cy.get('ul li').should('have.length.greaterThan', 0);
      } else {
        cy.contains('No coins found');
      }
    });
  });

  it('shows completed/not completed status for anonymous (no checkbox)', () => {
    cy.visit(`${BASE_URL}/`);
    cy.get('form[action*="toggle_completion"]').should('not.exist');
  });

  it('shows checkbox for authenticated user', () => {
    loginAs('user', 'userpass');
    cy.visit(`${BASE_URL}/`);
    cy.get('body').then(($body) => {
      if ($body.find('ul li').length > 0) {
        cy.get('input[type="checkbox"]').should('exist');
      }
    });
  });

  it('shows duty links inside coins', () => {
    cy.visit(`${BASE_URL}/`);
    cy.get('body').then(($body) => {
      const dutyLinks = $body.find('ul li a');
      if (dutyLinks.length > 0) {
        cy.get('ul li a').first().should('have.attr', 'href').and('match', /\/duties\//);
      }
    });
  });
});


describe('Duty detail page', () => {
  it('navigates to duty detail from home and shows duty info', () => {
    cy.visit(`${BASE_URL}/`);
    cy.get('body').then(($body) => {
      const firstDutyLink = $body.find('ul li a').first();
      if (firstDutyLink.length > 0) {
        cy.wrap(firstDutyLink).click();
        cy.get('h1').should('contain', 'Duty:');
        cy.contains('Back to Coins');
        cy.contains('Associated Coins');
      }
    });
  });
});


describe('Admin Coins CRUD', () => {
  const testCoinName = `TestCoin_${Date.now()}`;
  const updatedCoinName = `UpdatedCoin_${Date.now()}`;

  beforeEach(() => {
    loginAs('admin', 'adminpass');
  });

  after(() => {
    logout();
  });

  it('shows the Manage Coins admin page', () => {
    cy.visit(`${BASE_URL}/admin/coins`);
    cy.get('h1').contains('Manage Coins');
    cy.contains('Create Coin');
    cy.get('input[name="coin_name"]').should('exist');
    cy.get('button[type="submit"]').first().should('exist');
  });

  it('creates a new coin', () => {
    cy.visit(`${BASE_URL}/admin/coins`);
    cy.get('input[name="coin_name"]').first().clear().type(testCoinName);
    cy.get('form[action="/admin/coins/create"] button[type="submit"]').click();
    cy.url().should('include', '/admin/coins');
    cy.contains(testCoinName);
  });

  it('updates an existing coin', () => {
    cy.visit(`${BASE_URL}/admin/coins`);
    cy.contains(testCoinName)
      .closest('p')
      .next('form')
      .within(() => {
        cy.get('input[name="coin_name"]').clear().type(updatedCoinName);
        cy.get('button[type="submit"]').click();
      });
    cy.url().should('include', '/admin/coins');
    cy.contains(updatedCoinName);
  });

  it('deletes a coin', () => {
    cy.visit(`${BASE_URL}/admin/coins`);
    cy.contains(updatedCoinName)
      .closest('p')
      .nextAll('form')
      .filter('[action*="/delete"]')
      .first()
      .within(() => {
        cy.get('button[type="submit"]').click();
      });
    cy.url().should('include', '/admin/coins');
    cy.contains(updatedCoinName).should('not.exist');
  });

  it('redirects non-admin users away from admin coins', () => {
    logout();
    loginAs('user', 'userpass');
    cy.request({ url: `${BASE_URL}/admin/coins`, failOnStatusCode: false })
      .its('status')
      .should('eq', 403);
  });
});


describe('Admin Duties CRUD', () => {
  const testDutyName = `TestDuty_${Date.now()}`;
  const testDutyDesc = 'A duty created by Cypress';
  const updatedDutyName = `UpdatedDuty_${Date.now()}`;
  const updatedDutyDesc = 'Updated description by Cypress';

  beforeEach(() => {
    loginAs('admin', 'adminpass');
  });

  after(() => {
    logout();
  });

  it('shows the Manage Duties admin page', () => {
    cy.visit(`${BASE_URL}/admin/duties`);
    cy.get('h1').contains('Manage Duties');
    cy.contains('Create Duty');
    cy.get('input[name="duty_name"]').should('exist');
    cy.get('input[name="description"]').should('exist');
  });

  it('creates a new duty', () => {
    cy.visit(`${BASE_URL}/admin/duties`);
    cy.get('form[action="/admin/duties/create"]').within(() => {
      cy.get('input[name="duty_name"]').clear().type(testDutyName);
      cy.get('input[name="description"]').clear().type(testDutyDesc);
      cy.get('button[type="submit"]').click();
    });
    cy.url().should('include', '/admin/duties');
    cy.contains(testDutyName);
  });

  it('updates an existing duty', () => {
    cy.visit(`${BASE_URL}/admin/duties`);
    cy.contains(testDutyName)
      .closest('p')
      .next('form')
      .within(() => {
        cy.get('input[name="duty_name"]').clear().type(updatedDutyName);
        cy.get('input[name="description"]').clear().type(updatedDutyDesc);
        cy.get('button[type="submit"]').click();
      });
    cy.url().should('include', '/admin/duties');
    cy.contains(updatedDutyName);
  });

  it('deletes a duty', () => {
    cy.visit(`${BASE_URL}/admin/duties`);
    cy.contains(updatedDutyName)
      .closest('p')
      .nextAll('form')
      .filter('[action*="/delete"]')
      .first()
      .within(() => {
        cy.get('button[type="submit"]').click();
      });
    cy.url().should('include', '/admin/duties');
    cy.contains(updatedDutyName).should('not.exist');
  });

  it('redirects non-admin users away from admin duties', () => {
    logout();
    loginAs('user', 'userpass');
    cy.request({ url: `${BASE_URL}/admin/duties`, failOnStatusCode: false })
      .its('status')
      .should('eq', 403);
  });
});


describe('Admin Logs page', () => {
  beforeEach(() => {
    loginAs('admin', 'adminpass');
  });

  it('shows the logs page with table headers', () => {
    cy.visit(`${BASE_URL}/admin/logs`);
    cy.get('h1').contains('Last 100 Requests');
    cy.get('body').then(($body) => {
      if ($body.find('table').length > 0) {
        cy.get('table th').contains('Timestamp');
        cy.get('table th').contains('Method');
        cy.get('table th').contains('Path');
        cy.get('table th').contains('User');
        cy.get('table th').contains('IP');
      } else {
        cy.contains('No requests logged yet');
      }
    });
  });

  it('shows at least one log entry after navigating', () => {
    cy.visit(`${BASE_URL}/`);
    cy.visit(`${BASE_URL}/admin/logs`);
    cy.get('table tr').should('have.length.greaterThan', 1);
  });

  it('blocks anonymous access to logs', () => {
    logout();
    cy.visit(`${BASE_URL}/admin/logs`);
    cy.url().should('include', '/login');
  });
});