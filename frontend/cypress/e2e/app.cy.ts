describe("App shell", () => {
  it("loads the app root", () => {
    cy.visit("/");
    cy.get("#root").should("exist");
  });
});
