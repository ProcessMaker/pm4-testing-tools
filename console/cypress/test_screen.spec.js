describe('{testName}', () => {
  beforeEach(() => {
    cy.server();
    cy.visit('/');
  });

  it('Verify $TEST_NAME', () => {
    cy.loadFromJson('{testScreenFile}', 0);
    cy.get('[data-cy=mode-preview]').click();

    // Check the data of the screen
    cy.assertPreviewData({
    });
  });
});
