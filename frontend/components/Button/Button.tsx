"use client";

import React from "react";
import "./Button.scss";

export type ButtonColor = "orange" | "gray";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  text?: string;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  color?: ButtonColor;
}

export default function Button({
  text,
  onClick,
  color = "orange",
  children,
  className = "",
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={`Button Button--${color} ${className}`.trim()}
      onClick={onClick}
      {...props}
    >
      {text ?? children}
    </button>
  );
}
