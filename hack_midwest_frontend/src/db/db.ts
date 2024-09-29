export const projects = [
  { name: "GPT-4", id: "gpt4", state: "building", workers: [] },
  { name: "BERT", id: "bert", state: "building", workers: [] },
  { name: "T5", id: "t5", state: "building", workers: [] },
  {
    name: "RoBERTa",
    id: "roberta",
    state: "ready",
    workers: [
      {
        id: "i-0a1b2c3d4e5f67890",
        files: [{ name: "sampledata.csv" }, { name: "coolstuff.txt" }],
        status: "online",
      },
      {
        id: "i-1b2c3d4e5f6789012",
        files: [{ name: "bankdata.csv" }, { name: "profitdata.csv" }],
        status: "offline",
      },
      {
        id: "i-2c3d4e5f678901234",
        files: [{ name: "layoffs.txt" }],
        status: "online",
      },
      {
        id: "i-3d4e5f67890123456",
        files: [],
        status: "online",
      },
      {
        id: "i-4e5f6789012345678",
        files: [
          { name: "mangoprices.csv" },
          { name: "appleprices.csv" },
          { name: "bananas.csv" },
        ],
        status: "online",
      },
      {
        id: "i-5f678901234567890",
        files: [],
        status: "online",
      },
      {
        id: "i-6g789012345678901",
        files: [{ name: "averageincome.txt" }],
        status: "online",
      },
    ],
  },
  {
    name: "GPT-Neo",
    id: "gpt-neo",
    state: "ready",
    workers: [
      {
        id: "i-7h8i9j0k1l2m34567",
        files: [],
        status: "online",
      },
      {
        id: "i-8i9j0k1l2m3456789",
        files: [],
        status: "online",
      },
      {
        id: "i-9j0k1l2m345678901",
        files: [],
        status: "online",
      },
      {
        id: "i-0k1l2m34567890123",
        files: [],
        status: "online",
      },
      {
        id: "i-1l2m3456789012345",
        files: [],
        status: "online",
      },
      {
        id: "i-2m345678901234567",
        files: [],
        status: "online",
      },
      {
        id: "i-3n456789012345678",
        files: [],
        status: "online",
      },
    ],
  },
  {
    name: "ALBERT",
    id: "albert",
    state: "ready",
    workers: [
      {
        id: "i-4p5q6r7s8t9u01234",
        files: [],
        status: "online",
      },
      {
        id: "i-5q6r7s8t9u0123456",
        files: [],
        status: "online",
      },
      {
        id: "i-6r7s8t9u012345678",
        files: [],
        status: "restarting",
      },
      {
        id: "i-7s8t9u01234567890",
        files: [],
        status: "online",
      },
      {
        id: "i-8t9u0123456789012",
        files: [],
        status: "online",
      },
    ],
  },
  {
    name: "XLNet",
    id: "xlnet",
    state: "ready",
    workers: [
      {
        id: "i-9u0v1w2x3y4z56789",
        files: [],
        status: "online",
      },
      {
        id: "i-0v1w2x3y4z5678901",
        files: [],
        status: "online",
      },
      {
        id: "i-1w2x3y4z567890123",
        files: [],
        status: "online",
      },
      {
        id: "i-2x3y4z56789012345",
        files: [],
        status: "online",
      },
      {
        id: "i-3y4z5678901234567",
        files: [],
        status: "online",
      },
      {
        id: "i-4z567890123456789",
        files: [],
        status: "offline",
      },
    ],
  },
  { name: "BLOOM", id: "bloom", state: "ready", workers: [] },
  { name: "FLAN-T5", id: "flan-t5", state: "ready", workers: [] },
  { name: "LaMDA", id: "lamda", state: "ready", workers: [] },
];
