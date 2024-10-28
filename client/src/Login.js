import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Login = () => {
  const [username, setusername] = useState("");
  const [password, setpassword] = useState("");

  const navigate = useNavigate();

  const [authenticated, setauthenticated] = useState(localStorage.getItem("authenticated"));
  const handleSubmit = (e) => {
    e.preventDefault();
    const url = "http://127.0.0.1:5000/login";

    const response = axios
        .post(url, {
          username: username,
          password: password,
        })
        .then(function (response) {
          localStorage.setItem("access_token", response.data.access_token);
        });


    if (typeof localStorage.getItem("access_token") != "undefined") {
        setauthenticated(true);
        localStorage.setItem("authenticated", true);
        //localStorage.setItem("access_token", access_token);
        navigate("/");
    }
  };
  return (
    <div>
      <p>Welcome Back</p>
      <form onSubmit={handleSubmit}>
      <input
        type="text"
        name="Username"
        value={username}
        onChange={(e) => setusername(e.target.value)}
      />
      <input
        type="password"
        name="Password"
        onChange={(e) => setpassword(e.target.value)}
      />
      <input type="submit" value="Submit" />
      </form>
    </div>
  )
};

export default Login;