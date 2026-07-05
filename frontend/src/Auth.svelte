<script>
  import { onMount } from 'svelte'
  
  let currentPage = 'login' // 'login', 'register'
  let username = ''
  let password = ''
  let email = ''
  let error = ''
  let loading = false
  let showPassword = false
  let successMessage = ''
  
  // Sample credentials for demo
  const sampleCredentials = {
    username: 'demo',
    password: 'password123'
  }
  
  // Check if already logged in
  onMount(async () => {
    try {
      const response = await fetch('/api/check-auth', {
        credentials: 'include'
      })
      const data = await response.json()
      
      if (data.authenticated) {
        window.location.href = '/'
      }
    } catch (err) {
      console.error('Auth check failed:', err)
    }
  })
  
  function fillSampleCredentials() {
    username = sampleCredentials.username
    password = sampleCredentials.password
    successMessage = 'Sample credentials filled! Click Sign In to continue.'
    setTimeout(() => successMessage = '', 3000)
  }
  
  async function handleLogin() {
    if (!username || !password) {
      error = 'Please enter username and password'
      return
    }
    
    loading = true
    error = ''
    successMessage = ''
    
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ username, password })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        // Store welcome message in sessionStorage to show on main page
        sessionStorage.setItem('welcomeMessage', `Welcome back, ${data.username}! You are now signed in.`)
        window.location.href = '/'
      } else {
        error = data.error || 'Login failed'
      }
    } catch (err) {
      error = 'Network error. Please try again.'
    } finally {
      loading = false
    }
  }
  
  async function handleRegister() {
    if (!username || !password) {
      error = 'Please enter username and password'
      return
    }
    
    if (username.length < 3) {
      error = 'Username must be at least 3 characters'
      return
    }
    
    if (password.length < 6) {
      error = 'Password must be at least 6 characters'
      return
    }
    
    loading = true
    error = ''
    successMessage = ''
    
    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ username, password, email })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        // Store welcome message in sessionStorage to show on main page
        sessionStorage.setItem('welcomeMessage', `Welcome, ${data.username}! Your account has been created and you are now signed in.`)
        window.location.href = '/'
      } else {
        error = data.error || 'Registration failed'
      }
    } catch (err) {
      error = 'Network error. Please try again.'
    } finally {
      loading = false
    }
  }
  
  function handleSubmit() {
    if (currentPage === 'login') {
      handleLogin()
    } else {
      handleRegister()
    }
  }
</script>

<div class="auth-container">
  <div class="auth-card">
    <div class="auth-header">
      <h1>📚 Timetable Generator</h1>
      <p>Create and manage class timetables efficiently</p>
    </div>
    
    <div class="auth-tabs">
      <button 
        class="tab-btn" 
        class:active={currentPage === 'login'}
        on:click={() => currentPage = 'login'}
      >
        Sign In
      </button>
      <button 
        class="tab-btn" 
        class:active={currentPage === 'register'}
        on:click={() => currentPage = 'register'}
      >
        Register
      </button>
    </div>
    
    {#if currentPage === 'login'}
      <div class="sample-login">
        <button type="button" class="sample-btn" on:click={fillSampleCredentials}>
          ✨ Use Sample Credentials
        </button>
        <p class="sample-hint">Demo: demo / password123</p>
      </div>
    {/if}
    
    <form class="auth-form" on:submit|preventDefault={handleSubmit}>
      <div class="form-group">
        <label for="username">Username</label>
        <input
          id="username"
          type="text"
          bind:value={username}
          placeholder="Choose a username"
          required
          minlength="3"
        />
      </div>
      
      {#if currentPage === 'register'}
        <div class="form-group">
          <label for="email">Email (optional)</label>
          <input
            id="email"
            type="email"
            bind:value={email}
            placeholder="your@email.com"
          />
        </div>
      {/if}
      
      <div class="form-group">
        <label for="password">Password</label>
        <div class="password-input">
          {#if showPassword}
            <input
              id="password"
              type="text"
              bind:value={password}
              placeholder="Enter your password"
              required
              minlength={currentPage === 'register' ? 6 : 1}
            />
          {:else}
            <input
              id="password"
              type="password"
              bind:value={password}
              placeholder="Enter your password"
              required
              minlength={currentPage === 'register' ? 6 : 1}
            />
          {/if}
          <button
            type="button"
            class="toggle-password"
            on:click={() => showPassword = !showPassword}
          >
            {showPassword ? '👁️' : '🙈'}
          </button>
        </div>
      </div>
      
      {#if successMessage}
        <div class="success-message">
          ✅ {successMessage}
        </div>
      {/if}
      
      {#if error}
        <div class="error-message">
          ⚠️ {error}
        </div>
      {/if}
      
      <button 
        type="submit" 
        class="submit-btn"
        disabled={loading}
      >
        {loading ? 'Please wait...' : (currentPage === 'login' ? 'Sign In' : 'Register')}
      </button>
    </form>
    
    <div class="auth-footer">
      {#if currentPage === 'login'}
        <p>New to Timetable Generator? <button on:click={() => currentPage = 'register'} class="link-btn">Create an account</button></p>
      {:else}
        <p>Already have an account? <button on:click={() => currentPage = 'login'} class="link-btn">Sign in</button></p>
      {/if}
    </div>
  </div>
</div>

<style>
  .auth-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
  }
  
  .auth-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    padding: 2rem;
    width: 100%;
    max-width: 400px;
  }
  
  .auth-header {
    text-align: center;
    margin-bottom: 2rem;
  }
  
  .auth-header h1 {
    margin: 0 0 0.5rem 0;
    color: #333;
    font-size: 2rem;
  }
  
  .auth-header p {
    margin: 0;
    color: #666;
    font-size: 0.9rem;
  }
  
  .auth-tabs {
    display: flex;
    margin-bottom: 2rem;
    border-bottom: 1px solid #e0e0e0;
  }
  
  .tab-btn {
    flex: 1;
    padding: 1rem;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 1rem;
    color: #666;
    border-bottom: 2px solid transparent;
    transition: all 0.3s ease;
  }
  
  .tab-btn.active {
    color: #667eea;
    border-bottom-color: #667eea;
  }
  
  .auth-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .form-group label {
    font-weight: 600;
    color: #333;
    font-size: 0.9rem;
  }
  
  .form-group input {
    padding: 0.75rem;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
  }
  
  .form-group input:focus {
    outline: none;
    border-color: #667eea;
  }
  
  .password-input {
    position: relative;
  }
  
  .toggle-password {
    position: absolute;
    right: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.2rem;
  }
  
  .error-message {
    background: #fee;
    color: #c33;
    padding: 0.75rem;
    border-radius: 8px;
    text-align: center;
    font-size: 0.9rem;
  }
  
  .success-message {
    background: #efe;
    color: #3c3;
    padding: 0.75rem;
    border-radius: 8px;
    text-align: center;
    font-size: 0.9rem;
  }
  
  .sample-login {
    text-align: center;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px dashed #667eea;
  }
  
  .sample-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s ease;
  }
  
  .sample-btn:hover {
    transform: translateY(-2px);
  }
  
  .sample-hint {
    margin: 0.5rem 0 0 0;
    color: #666;
    font-size: 0.8rem;
  }
  
  .submit-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 1rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s ease;
  }
  
  .submit-btn:hover:not(:disabled) {
    transform: translateY(-2px);
  }
  
  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .auth-footer {
    text-align: center;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #e0e0e0;
  }
  
  .auth-footer p {
    margin: 0;
    color: #666;
    font-size: 0.9rem;
  }
  
  .link-btn {
    background: none;
    border: none;
    color: #667eea;
    cursor: pointer;
    font-weight: 600;
    text-decoration: underline;
  }
  
  .link-btn:hover {
    color: #764ba2;
  }
</style>
