import unittest
from unittest.mock import patch
from mutants import DnaSequence, Matrix, app

class TestMutantValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.mutant_dna = [['A','A','A','A'],['A','C','A','G'],['A','C','A','G'],['A','C','A','G']]
        self.human_dna = [['G','A','T','A'],['G','C','A','G']]
        self.dna = DnaSequence()
        self.matrix = Matrix()

        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.human_payload = { "dna":["ATGCGA","CCGTCC","TTATGT","AGAAGG","CCGCTA","TCACTG"] }  
        self.mutant_up_right_payload = { "dna": ["AAGCGC","CGCTTC","ACATGT","CGAAGG","AAGTGC"] } 
        self.mutant_vertical_down_payload = { "dna":["AAGTGC","AGGTGC","ATATGT","AGAAGG","TCACTG","TCACTG"] }  
        self.mutant_horizontal_right_payload = { "dna":["AAAAGC","AGGTGC","ATATGT","AGAAGG","TCACTG","TCACTG"] }  
        self.mutant_down_right_payload = { "dna":["AAGTGC","AAGTGC","ATATGT","AGTAGG","TCACTG","TCACTG"] }  

    def tearDown(self):
        pass

    def test_dna_validation_is_mutant_true(self):
        is_mutant = self.dna.is_mutant(self.mutant_dna)
        self.assertTrue(is_mutant)

    def test_dna_validation_is_mutant_false(self):
        is_mutant = self.dna.is_mutant(self.human_dna)
        self.assertFalse(is_mutant)

    def test_build_matrix_from_dna_sequence_sample(self):
        matrix = self.matrix.build_matrix_from_dna_sample(['AAA','BBB'])
        self.assertEqual([['A','A','A'],['B','B','B']], matrix)

    def test_select_up_right_diagonal_from_matrix(self):
        result = self.matrix.select_up_right_diagonal_from_matrix(2, ['ABC','DEF','GHI'], 0, 2)
        self.assertEqual('GE', result)

    def test_select_up_right_diagonal_from_matrix_out_of_range(self):
        result = self.matrix.select_up_right_diagonal_from_matrix(2, ['ABC','DEF','GHI'], 3, 3)
        self.assertFalse(result)

    def test_select_down_right_diagonal_from_matrix(self):
        result = self.matrix.select_down_right_diagonal_from_matrix(2, ['ABC','DEF','GHI'], 0, 0)
        self.assertEqual('AE', result)

    def test_select_down_right_diagonal_from_matrix_out_of_range(self):
        result = self.matrix.select_down_right_diagonal_from_matrix(2, ['ABC','DEF','GHI'], 3, 3)
        self.assertFalse(result)

    def test_select_horizontal_to_right_from_matrix(self):
        result = self.matrix.select_horizontal_to_right_from_matrix(2, ['ABC','DEF','GHI'], 1, 1)
        self.assertEqual('EF', result)

    def test_select_horizontal_to_right_from_matrix_out_of_range(self):
        result = self.matrix.select_horizontal_to_right_from_matrix(2, ['ABC','DEF','GHI'], 3, 3)
        self.assertFalse(result)

    def test_select_vertical_to_down_from_matrix(self):
        result = self.matrix.select_vertical_to_down_from_matrix(2, ['ABC','DEF','GHI'], 1, 1)
        self.assertEqual('EH', result)

    def test_select_vertical_to_down_from_matrix_out_of_range(self):
        result = self.matrix.select_vertical_to_down_from_matrix(2, ['ABC','DEF','GHI'], 3, 3)
        self.assertFalse(result)

    @patch("mutants.Dna")
    def test_mutant_post_response_false(self, dna):
        response = self.client.post('/mutant', json=self.human_payload)
        expected_resp = {'isMutant':False, 'updatedStats': False, 'savedToDatabase': False}
        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(response.get_json(), expected_resp)

    @patch("mutants.Dna")
    def test_mutant_up_right_post_response(self, dna):
        expected_resp = {'isMutant':True, 'updatedStats': False, 'savedToDatabase': False}

        response = self.client.post('/mutant', json=self.mutant_up_right_payload)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.get_json(), expected_resp)

        response = self.client.post('/mutant', json=self.mutant_vertical_down_payload)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.get_json(), expected_resp)

        response = self.client.post('/mutant', json=self.mutant_horizontal_right_payload)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.get_json(), expected_resp)

        response = self.client.post('/mutant', json=self.mutant_down_right_payload)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.get_json(), expected_resp)



    def test_dummy_get_response(self):
        response = self.client.get('/dummy')
        expected_resp = {'message': 'ok'}
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.get_json(), expected_resp)

    def test_hello_world_get_response(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @patch("mutants.Dna")
    def test_add_dna_to_database_true(self, dna):
        added = dna.add_to_database(self.mutant_dna, True)
        self.assertTrue(added)
#####
    # Tests for update stats through another service
    # def test_update_stats_status_code_200(self):
    #     with patch('mutants.requests.put') as mocked_put:
    #         mocked_put.return_value.status_code = 200
    #         is_mutant = True

    #         update_stats = self.dna.update_stats(is_mutant)
    #         mocked_put.assert_called_with('http://microservicios.stats.com/stats')
    #         self.assertEqual(update_stats, 200)

    # def test_update_stats_status_code_500(self):
    #     with patch('mutants.requests.put') as mocked_put:
    #         mocked_put.return_value.status_code = 500
    #         is_mutant = True

    #         update_stats = self.dna.update_stats(is_mutant)
    #         mocked_put.assert_called_with('http://microservicios.stats.com/stats')
    #         self.assertEqual(update_stats, 500)


if __name__ == '__main__':
    unittest.main()