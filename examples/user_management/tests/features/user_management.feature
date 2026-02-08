Feature: User Management

  Scenario: Create a new user with valid credentials
    Given the user database is empty
    When I create a user with email "alice@example.com" and password "secure123"
    Then the user should be created successfully
    And the password should be hashed (not stored as plaintext)
    And the user should have ID greater than 0

  Scenario: Reject duplicate email
    Given the user database is empty
    And I create a user with email "alice@example.com" and password "secure123"
    When I attempt to create another user with the same email
    Then user creation should fail
    And an appropriate error message should be returned

  Scenario: Fetch user by ID
    Given the user database is empty
    And I create a user with email "bob@example.com" and password "bobpass"
    When I fetch the user using their ID
    Then I should receive the user details
    And the email should match "bob@example.com"
    And the password should not be included in the response

  Scenario: Update user email
    Given the user database is empty
    And I create a user with email "charlie@example.com" and password "charpass"
    When I update the user's email to "charlie.new@example.com"
    Then the update should succeed
    And fetching the user should show the new email

  Scenario: Delete user
    Given the user database is empty
    And I create a user with email "dave@example.com" and password "davepass"
    When I delete the user
    Then the user should no longer exist
    And fetching the deleted user should return an error