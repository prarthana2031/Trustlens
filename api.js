import { predict } from "./api";

function App() {

  const handleClick = async () => {
    const result = await predict({ input: "test" });
    console.log(result);
  };

  return (
    <button onClick={handleClick}>
      Test API
    </button>
  );
}

export default App;
