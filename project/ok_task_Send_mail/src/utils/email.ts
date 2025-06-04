// src/utils/email.ts
import nodemailer from 'nodemailer';

export const sendEmail = (to: string, subject: string, text: string): void => {
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.GMAIL_USER,
      pass: process.env.GMAIL_APP_PASSWORD,
    },
  });

  const mailOptions = {
    from: 'your.email@gmail.com',
    to,
    subject,
    text,
  };

  transporter.sendMail(mailOptions, (error, info) => {
    if (error) console.error('Error sending email:', error);
    else console.log('Email sent:', info.response);
  });
};
