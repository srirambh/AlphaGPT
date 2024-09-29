import ModelDashboard from "./model";
import { Route } from "react-router-dom";
import EditRoutes from "./edit";
export default (
  <Route path=":id">
    <Route index element={<ModelDashboard />} />
    {EditRoutes}
  </Route>
);
