type Arg = number | ['*', number];

type Instruction =
  // with args
  | [
      string, // opcode
      Arg // argument
    ]
  // argless
  | [string];

type Program = {
  instructions: Instruction[];
};

const program: Program = {
  instructions: [
    // hello world
    ['load_acc', 72],  // Load 'H' (ASCII 72) into accumulator
    ['out', 1],  // Print the character in the accumulator
    ['load_acc', 101],  // Load 'e'
    ['out', 1],
    ['load_acc', 108],  // Load 'l'
    ['out', 1],
    ['load_acc', 108],  // Load 'l'
    ['out', 1],
    ['load_acc', 111],  // Load 'o'
    ['out', 1],
    ['load_acc', 44],  // Load comma
    ['out', 1],
    ['load_acc', 32],  // Load space
    ['out', 1],
    ['load_acc', 119],  // Load 'w'
    ['out', 1],
    ['load_acc', 111],  // Load 'o'
    ['out', 1],
    ['load_acc', 114],  // Load 'r'
    ['out', 1],
    ['load_acc', 108],  // Load 'l'
    ['out', 1],
    ['load_acc', 100],  // Load 'd'
    ['out', 1],
    ['load_acc', 33],  // Load exclamation mark
    ['out', 1]
    ['halt']
  ],
};
