// src/pages/AuthPage.js
import React, { useState, useContext } from 'react';
import { CognitoUserPool, CognitoUser, AuthenticationDetails } from 'amazon-cognito-identity-js';
import { cognitoConfig } from '../cognitoConfig';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../AuthContext';

const AuthPage = () => {
  const { setIsLogged } = useContext(AuthContext);
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [givenName, setGivenName] = useState('');
  const [surname, setSurname] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [isVerificationStep, setIsVerificationStep] = useState(false);
  const navigate = useNavigate();

  const toggleAuthMode = () => {
    setIsLogin(!isLogin);
    setIsVerificationStep(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isLogin) {
      handleLogin();
    } else {
      handleSignUp();
    }
  };

  const handleSignUp = () => {
    const userPool = new CognitoUserPool({
      UserPoolId: cognitoConfig.UserPoolId,
      ClientId: cognitoConfig.ClientId,
    });

    const attributeList = [
      { Name: 'given_name', Value: givenName },
      { Name: 'family_name', Value: surname },
    ];

    userPool.signUp(email, password, attributeList, null, (err, result) => {
      if (err) {
        alert(err.message || JSON.stringify(err));
        return;
      }
      setIsVerificationStep(true);
    });
  };

  const handleVerification = (e) => {
    e.preventDefault();

    const userPool = new CognitoUserPool({
      UserPoolId: cognitoConfig.UserPoolId,
      ClientId: cognitoConfig.ClientId,
    });

    const userData = {
      Username: email,
      Pool: userPool,
    };

    const cognitoUser = new CognitoUser(userData);

    cognitoUser.confirmRegistration(verificationCode, true, (err, result) => {
      if (err) {
        if (err.message === 'Unrecognizable lambda output') {
          alert('Verification successful! Redirecting to home.');
          setIsLogged(true); // Set isLogged to true after successful verification
          navigate('/home');
        } else {
          alert(err.message || JSON.stringify(err));
        }
        return;
      }
      alert('Verification successful! Redirecting to home.');
      setIsVerificationStep(false);
      setIsLogin(true);
      setIsLogged(true); // Set isLogged to true after successful verification
      navigate('/home');
    });
  };

  const handleLogin = () => {
    const userPool = new CognitoUserPool({
      UserPoolId: cognitoConfig.UserPoolId,
      ClientId: cognitoConfig.ClientId,
    });

    const userData = {
      Username: email,
      Pool: userPool,
    };

    const cognitoUser = new CognitoUser(userData);
    const authenticationDetails = new AuthenticationDetails({
      Username: email,
      Password: password,
    });

    cognitoUser.authenticateUser(authenticationDetails, {
      onSuccess: (result) => {
        alert('Login successful!');
        setIsLogged(true); // Set isLogged to true after successful login
        navigate('/home');
      },
      onFailure: (err) => {
        alert(err.message || JSON.stringify(err));
      },
    });
  };

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>{isVerificationStep ? 'Enter Verification Code' : isLogin ? 'Login' : 'Sign Up'}</h2>
        {isVerificationStep ? (
          <form onSubmit={handleVerification}>
            <div className="form-group">
              <label htmlFor="verificationCode">Verification Code:</label>
              <input
                type="text"
                id="verificationCode"
                name="verificationCode"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                required
              />
            </div>
            <button type="submit">Verify</button>
          </form>
        ) : (
          <form onSubmit={handleSubmit}>
            {!isLogin && (
              <>
                <div className="form-group">
                  <label htmlFor="givenName">Given Name:</label>
                  <input
                    type="text"
                    id="givenName"
                    name="givenName"
                    value={givenName}
                    onChange={(e) => setGivenName(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="surname">Surname:</label>
                  <input
                    type="text"
                    id="surname"
                    name="surname"
                    value={surname}
                    onChange={(e) => setSurname(e.target.value)}
                    required
                  />
                </div>
              </>
            )}
            <div className="form-group">
              <label htmlFor="email">Email:</label>
              <input
                type="email"
                id="email"
                name="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password:</label>
              <input
                type="password"
                id="password"
                name="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit">{isLogin ? 'Login' : 'Sign Up'}</button>
          </form>
        )}
        {!isVerificationStep && (
          <p onClick={toggleAuthMode}>
            {isLogin ? "Don't have an account? Sign Up" : 'Already have an account? Login'}
          </p>
        )}
      </div>
    </div>
  );
};

export default AuthPage;
