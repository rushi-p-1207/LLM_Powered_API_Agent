const decoder = new TextDecoder();
const code = await Deno.readAll(Deno.stdin);

try {
  const userCode = decoder.decode(code);

  // Execute user code in strict sandbox
  const fn = new Function(`
    "use strict";
    ${userCode}
  `);

  const result = fn();

  if (result !== undefined) {
    console.log(result);
  }
} catch (err) {
  console.error("Sandbox Error:", err.message);
}
