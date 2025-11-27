describe('Landing page', () => {
  it('It should show a way for users to create all the duties for the automate coin', () => {
    cy.visit('/')
    cy.contains('Enter Duty Number').should('be.visible')
    cy.contains('Enter Duty Description').should('be.visible')
    cy.contains('Enter KSBs').should('be.visible')
    cy.contains("Create Duty").should('be.visible')
    cy.contains("No duties created yet")
})
})

describe('Adding duties', ()=>{
    it('It should allow users to create a duty', ()=>{
        cy.visit('/')
        cy.get('input[name="number"]').type('Duty Number')
        cy.get('input[name="description"]').type('Duty Description')
        cy.get('input[name="ksbs"]').type('Duty KSB')

        cy.get('button[type="submit"]').click()

        cy.contains('Duty Number')
        cy.contains('Duty Description')
        cy.contains('Duty KSB')
    })
    it('It should allow users to add multiple duties', ()=>{
        cy.visit('/')

        cy.get('input[name="number"]').type('Another Duty Number')
        cy.get('input[name="description"]').type('Another Duty Description')
        cy.get('input[name="ksbs"]').type('Another Duty KSB')

        cy.get('button[type="submit"]').click()

        cy.get('input[name="number"]').type('Duty Number')
        cy.get('input[name="description"]').type('Duty Description')
        cy.get('input[name="ksbs"]').type('Duty KSB')

        cy.get('button[type="submit"]').click()
 
        cy.contains('Duty Number')
        cy.contains('Duty Description')
        cy.contains('Duty KSB')

        cy.contains('Another Duty Number')
        cy.contains('Another Duty Description')
        cy.contains('Another Duty KSB')
    })
})