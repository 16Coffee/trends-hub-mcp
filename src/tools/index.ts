export const getTools = () => {
  return Promise.all(
    [
      import("./bilibili"),
    ]
  )
}