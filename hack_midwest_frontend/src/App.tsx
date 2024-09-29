import { Route, Routes } from "react-router-dom";
import HomeRoutes from "@/routes/home";
import NoMatch from "@/routes/nomatch";

function App() {
  return (
    <Routes>
      {HomeRoutes}
      <Route path="*" element={<NoMatch />} />
    </Routes>
  );
}

export default App;
