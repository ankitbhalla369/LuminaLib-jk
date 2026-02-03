const nextJest = require('next/jest')
const createJestConfig = nextJest({ dir: './' })
module.exports = createJestConfig({
  testEnvironment: 'jsdom',
  testPathIgnorePatterns: ['node_modules', '.next'],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
})
