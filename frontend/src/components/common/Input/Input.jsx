import React from 'react';
import PropTypes from 'prop-types';
import './Input.css';

/**
 * Input component for form fields
 */
const Input = ({
  id,
  label,
  type = 'text',
  value,
  onChange,
  disabled = false,
  error = '',
  ...props
}) => {
  return (
    <div className="form-group">
      {label && <label htmlFor={id}>{label}</label>}
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        disabled={disabled}
        className="input"
        {...props}
      />
      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

Input.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string,
  type: PropTypes.string,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
  error: PropTypes.string
};

export default Input;
