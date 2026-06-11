import unittest
from approvals.checker import ApprovalChecker

class TestChecker(unittest.TestCase):
    def test_assess_risk(self):
        c = ApprovalChecker()
        self.assertEqual(c._assess_risk(10**40, '0x1234'), 'high')
        self.assertEqual(c._assess_risk(100, '0x1234'), 'low')
    
    def test_pad_address(self):
        c = ApprovalChecker()
        padded = c._pad_address('0x1234567890abcdef')
        self.assertEqual(len(padded), 66)

if __name__ == '__main__':
    unittest.main()
