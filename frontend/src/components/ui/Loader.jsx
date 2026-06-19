import './Loader.css';

export default function Loader({ message = 'Loading...' }) {
  return (
    <div className="loader-overlay">
      <div className="spinner"></div>
      <p className="loader-message">{message}</p>
    </div>
  );
}
