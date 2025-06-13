import type { NextApiRequest, NextApiResponse } from 'next'
import axios from 'axios'

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000'



export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const response = await axios.post(`${BACKEND_URL}/chat`, req.body, {
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000, // 60 second timeout
    })

    res.status(200).json(response.data)
  } catch (error: any) {
    console.error('Error calling backend:', error.message)

    if (error.response) {
      // Backend returned an error response
      res.status(error.response.status).json({
        error: error.response.data?.detail || 'Backend error'
      })
    } else if (error.code === 'ECONNREFUSED') {
      // Backend is not running
      res.status(503).json({
        error: 'Backend service is not available. Please make sure the backend is running.'
      })
    } else {
      // Other errors
      res.status(500).json({
        error: 'Failed to process request'
      })
    }
  }
}
