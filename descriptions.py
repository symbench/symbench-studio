PROBLEM_DESCRIPTIONS = {
    "bnh": {
        "objectives": [
            r"\textit{Minimize} \quad f_{1}(\mathbf{x}) = 4x_1^2 + 4x_2^2",
            r"\textit{Minimize} \quad f_{2}(\mathbf{x}) = (x_1 - 5)^2 + (x_2 - 5)^2"
        ],
        "constraints": [
            r"C_{1}(\mathbf{x}) \equiv (x_1 - 5)^2 + x_{2}^2 \leq 25",
            r"C_{2}(\mathbf{x}) \equiv (x_1 - 8)^2 + (x_2 + 3)^2 \geq 7.7",
            r"0 \leq x_1 \leq 5, \quad 0 \leq x_2 \leq 3"
        ]
    },
    "osy": {
        "objectives": [
            r"\textit{Minimize} \quad f_{1}(\mathbf{x}) = -[25(x_1 - 2)^2 - (x_2 - 2)^2 - (x_3 - 1)^2 - (x_4 - 4)^2 - (x_5 - 1)^2]",
            r"\textit{Minimize} \quad f_{2}(\mathbf{x}) = x_1^2 + x_2^2 + x_3^2 + x_4^2 + x_5^2 + x_6^2"
        ],
        "constraints": [
            r"C_{1}(\mathbf{x}) \equiv x_1 + x_2 - 2 \geq 0",
            r"C_{2}(\mathbf{x}) \equiv 6 - x_1 - x_2 \geq 0",
            r"C_{3}(\mathbf{x}) \equiv 2 - x_2 + x_1 \geq 0",
            r"C_{4}(\mathbf{x}) \equiv 2 - x_1 + 3x_2 \geq 0",
            r"C_{5}(\mathbf{x}) \equiv 4 - (x_3 - 3)^2 - x_4 \geq 0",
            r"C_{6}(\mathbf{x}) \equiv (x_5 - 3)^2 + x_6 - 4 \geq 0",
            r"0 \leq x_1, x_2, x_6 \leq 10, \quad 1 \leq x_3, x_5 \leq 5, \quad 0 \leq x_4 \leq 6",
        ]
    },
    "tnk": {
        "objectives": [
            r"\textit{Minimize} \quad f_{1}(\mathbf{x}) = x_1c",
            r"\textit{Minimize} \quad f_{2}(\mathbf{x}) = x_2"
        ],
        "constraints": [
            r"C_{1}(\mathbf{x}) \equiv x_1^2 + x_2^2 - 1 - 0.1 \cos(16 \arctan(\frac{x_1}{x_2})) \geq 0",
            r"C_{2}(\mathbf{x}) \equiv (x_1 - 0.5)^2 + (x_2 - 0.5)^2 \leq 0.5",
            r"0 \leq x_1, x_2 \leq \pi"
        ]
    }
}

PROBLEM_PARAMETERS = {
    "BNH": {},
    "OSY": {},
    "TNK": {}
}