describe('{testName}', () => {
  beforeEach(() => {
    cy.server();
    cy.visit('/');
  });

  it('Verify {testName}', () => {
    cy.loadFromJson('{testScreenFile}', 0);
    // set init screen test data
    // cy.setPreviewDataInput({person: []});
    cy.get('[data-cy=mode-preview]').click();

    // cy.get('[data-cy=preview-content] [name="form_input_1"]').should('not.be.visible');
    // cy.get('[data-cy=preview-content] [name=form_checkbox_1]').click();
    // cy.get('[data-cy=preview-content] [name="select1.form_input_1"]').clear().type('it works');

    // Check the data of the screen
    cy.assertPreviewData({
    });
  });
});
