import { Route } from "react-router-dom";
import Home from "./home";
import Layout from "./layout";
import ModelRoutes from "./[model]";

export default (
  <>
    <Route path="/" element={<Layout />}>
      <Route index element={<Home />} />
      {ModelRoutes}
    </Route>
  </>
);
