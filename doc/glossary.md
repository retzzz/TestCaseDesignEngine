## DO-178C:

**Condition**: A Boolean expression containing no Boolean operators except for the unary operator(NOT).

**Decision**: A Boolean expression composed of conditions and zero or more Boolean operators. If a condition appears more than once in a decision, each occurrence is a distinct condition.

**Modified condition/decision coverage**: Every point of entry and exit in the program has been invoked at least once, every condition in a decision in the program has taken all possible outcomes at least once, every decision in the program has taken all possible outcomes at least once, and each condition in a decision has been shown to independently affect that decision's outcome. A condition is shown to independently affect a decision's outcome by: (1) varying just that condition while holding fixed all other possible conditions, or (2) varying just that condition while holding fixed all other possible conditions that could affect the outcome.

**Normal Range Test Cases**: 4 kinds of test cases that are described in section 6.4.2.1. in DO-178C
    a. Real and integer input variables should be exercised using valid equivalence classes and boundary values.
    b. For time-related functions, such as filters, integrators and delays, multiple iterations of the code should be performed to check the characteristics of the function in context.
    c. For state transitions, test cases should be developed to exercise the transitions possible during normal operation.
    d. For software requirements expressed by logic equations, the normal range test cases should verify the variable usage and the Boolean operators.

**Robustness Test Cases**: 7 kinds of test cases that are described in section 6.4.2.2. in DO-178C
    a. Real and integer variables should be exercised using equivalence class selection of invalid values.
    b. System initialization should be exercised during abnormal conditions.
    c. The possible failure modes of the incoming data should be determined, especially complex, digital data strings from an external system.
    d. For loops where the loop count is a computed value, test cases should be developed to attempt to compute out-of-range loop count values, and thus demonstrate the robustness of the loop-related code.
    e. A check should be made to ensure that protection mechanisms for exceeded frame times respond correctly.
    f. For time-related functions, such as filters, integrators and delays, test cases should be developed for arithmetic overflow protection mechanisms.
    g. For state transitions, test cases should be developed to provoke transitions that are not allowed by the software requirements.

## This Tool:

**Parameter**: a variable that can be set value directly by a test case. The type of a parameter can be boolean, integter, or real.

**Condition**: same as 'Condition' in DO-178C, it could be one of (1) a boolean type parameter, (2) a Compare Expression, (3) a Unary operation with 'not' as operator and its operand is a boolean type parameter, a Compare Expression, or another Unary 'not' operation. It can also be called 'Leaf Node'.

**Input Set**: A map from each parameter to a specific value.

**Condition Truth Assignments**: When a input set is specified, a condition should be calculated to true or false (hereinafter T=true or F=false). It can be called a condition truth assignment or truth assignment in short. It is a result of Input Set.

**Output**: The things that will be done when a input set is specified.

**Output Statements**: The statements what will be executed when a input set is specified. Multiple Output Statements are considered same Output if they are same. Because the different statements can do same thing.

**Test Case**: A map from a Input Set to a Output. Test Case must specify a input set and verify if the correct output is done.

**Free Condition**: In a Test Case, when varying just this Condition, while holding fixed all other conditions, the Output keep same.

**Independent Condition**: In a Test Case, when varying just this Condition, while holding fixed all other conditions except Free Condtions, the Output will change. Each Test Case has one or more Independent Condition. Each Condition need to be Independent Condition in at least 2 Test Cases, with its value T and F seperately.


