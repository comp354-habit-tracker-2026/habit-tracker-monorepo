const styleProxy = new Proxy(
  {},
  {
    get: (_target, property) => (typeof property === "string" ? property : ""),
  }
);

export default styleProxy;
