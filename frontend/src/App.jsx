import { BrowserRouter, Routes, Route } from "react-router-dom";

import Cars from "./Cars";
import Login from "./Login";
import ProtectedRoute from "./ProtectedRoute";

function App() {

  return (

    <BrowserRouter>

      <Routes>

        <Route path="/login" element={<Login />} />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Cars />
            </ProtectedRoute>
          }
        />

      </Routes>

    </BrowserRouter>

  );
}

export default App;