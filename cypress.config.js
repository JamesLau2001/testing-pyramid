const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    defaultCommandTimeout: 8000,
    pageLoadTimeout: 30000,
    uncaughtExceptions: false,
  },
});